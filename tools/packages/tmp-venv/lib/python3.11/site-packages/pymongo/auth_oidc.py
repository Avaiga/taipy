# Copyright 2023-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MONGODB-OIDC Authentication helpers."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, MutableMapping, Optional

import bson
from bson.binary import Binary
from bson.son import SON
from pymongo.errors import ConfigurationError, OperationFailure

if TYPE_CHECKING:
    from pymongo.auth import MongoCredential
    from pymongo.pool import Connection


@dataclass
class _OIDCProperties:
    request_token_callback: Optional[Callable[..., dict]]
    provider_name: Optional[str]
    allowed_hosts: list[str]


"""Mechanism properties for MONGODB-OIDC authentication."""

TOKEN_BUFFER_MINUTES = 5
CALLBACK_TIMEOUT_SECONDS = 5 * 60
CALLBACK_VERSION = 1


def _get_authenticator(
    credentials: MongoCredential, address: tuple[str, int]
) -> _OIDCAuthenticator:
    if credentials.cache.data:
        return credentials.cache.data

    # Extract values.
    principal_name = credentials.username
    properties = credentials.mechanism_properties

    # Validate that the address is allowed.
    if not properties.provider_name:
        found = False
        allowed_hosts = properties.allowed_hosts
        for patt in allowed_hosts:
            if patt == address[0]:
                found = True
            elif patt.startswith("*.") and address[0].endswith(patt[1:]):
                found = True
        if not found:
            raise ConfigurationError(
                f"Refusing to connect to {address[0]}, which is not in authOIDCAllowedHosts: {allowed_hosts}"
            )

    # Get or create the cache data.
    credentials.cache.data = _OIDCAuthenticator(username=principal_name, properties=properties)
    return credentials.cache.data


@dataclass
class _OIDCAuthenticator:
    username: str
    properties: _OIDCProperties
    refresh_token: Optional[str] = field(default=None)
    access_token: Optional[str] = field(default=None)
    idp_info: Optional[dict] = field(default=None)
    token_gen_id: int = field(default=0)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def get_current_token(self, use_callback: bool = True) -> Optional[str]:
        properties = self.properties

        # TODO: DRIVERS-2672, handle machine callback here as well.
        cb = properties.request_token_callback if use_callback else None
        cb_type = "human"

        prev_token = self.access_token
        if prev_token:
            return prev_token

        if not use_callback and not prev_token:
            return None

        if not prev_token and cb is not None:
            with self.lock:
                # See if the token was changed while we were waiting for the
                # lock.
                new_token = self.access_token
                if new_token != prev_token:
                    return new_token

                # TODO: DRIVERS-2672 handle machine callback here.
                if cb_type == "human":
                    context = {
                        "timeout_seconds": CALLBACK_TIMEOUT_SECONDS,
                        "version": CALLBACK_VERSION,
                        "refresh_token": self.refresh_token,
                    }
                    resp = cb(self.idp_info, context)

                    self.validate_request_token_response(resp)

                self.token_gen_id += 1

        return self.access_token

    def validate_request_token_response(self, resp: Mapping[str, Any]) -> None:
        # Validate callback return value.
        if not isinstance(resp, dict):
            raise ValueError("OIDC callback returned invalid result")

        if "access_token" not in resp:
            raise ValueError("OIDC callback did not return an access_token")

        expected = ["access_token", "refresh_token", "expires_in_seconds"]
        for key in resp:
            if key not in expected:
                raise ValueError(f'Unexpected field in callback result "{key}"')

        self.access_token = resp["access_token"]
        self.refresh_token = resp.get("refresh_token")

    def principal_step_cmd(self) -> SON[str, Any]:
        """Get a SASL start command with an optional principal name"""
        # Send the SASL start with the optional principal name.
        payload = {}

        principal_name = self.username
        if principal_name:
            payload["n"] = principal_name

        return SON(
            [
                ("saslStart", 1),
                ("mechanism", "MONGODB-OIDC"),
                ("payload", Binary(bson.encode(payload))),
                ("autoAuthorize", 1),
            ]
        )

    def auth_start_cmd(self, use_callback: bool = True) -> Optional[SON[str, Any]]:
        # TODO: DRIVERS-2672, check for provider_name in self.properties here.
        if self.idp_info is None:
            return self.principal_step_cmd()

        token = self.get_current_token(use_callback)
        if not token:
            return None
        bin_payload = Binary(bson.encode({"jwt": token}))
        return SON(
            [
                ("saslStart", 1),
                ("mechanism", "MONGODB-OIDC"),
                ("payload", bin_payload),
            ]
        )

    def run_command(
        self, conn: Connection, cmd: MutableMapping[str, Any]
    ) -> Optional[Mapping[str, Any]]:
        try:
            return conn.command("$external", cmd, no_reauth=True)  # type: ignore[call-arg]
        except OperationFailure:
            self.access_token = None
            raise

    def reauthenticate(self, conn: Connection) -> Optional[Mapping[str, Any]]:
        """Handle a reauthenticate from the server."""
        # First see if we have the a newer token on the authenticator.
        prev_id = conn.oidc_token_gen_id or 0
        # If we've already changed tokens, make one optimistic attempt.
        if (prev_id < self.token_gen_id) and self.access_token:
            try:
                return self.authenticate(conn)
            except OperationFailure:
                pass

        self.access_token = None

        # TODO: DRIVERS-2672, check for provider_name in self.properties here.
        # If so, we clear the access token and return finish_auth.

        # Next see if the idp info has changed.
        prev_idp_info = self.idp_info
        self.idp_info = None
        cmd = self.principal_step_cmd()
        resp = self.run_command(conn, cmd)
        assert resp is not None
        server_resp: dict = bson.decode(resp["payload"])
        if "issuer" in server_resp:
            self.idp_info = server_resp

        # Handle the case of changed idp info.
        if self.idp_info != prev_idp_info:
            self.access_token = None
            self.refresh_token = None

        # If we have a refresh token, try using that.
        if self.refresh_token:
            try:
                return self.finish_auth(resp, conn)
            except OperationFailure:
                self.refresh_token = None
                # If that fails, try again without the refresh token.
                return self.authenticate(conn)

        # If we don't have a refresh token, just try once.
        return self.finish_auth(resp, conn)

    def authenticate(self, conn: Connection) -> Optional[Mapping[str, Any]]:
        ctx = conn.auth_ctx
        cmd = None

        if ctx and ctx.speculate_succeeded():
            resp = ctx.speculative_authenticate
        else:
            cmd = self.auth_start_cmd()
            assert cmd is not None
            resp = self.run_command(conn, cmd)

        assert resp is not None
        if resp["done"]:
            conn.oidc_token_gen_id = self.token_gen_id
            return None

        server_resp: dict = bson.decode(resp["payload"])
        if "issuer" in server_resp:
            self.idp_info = server_resp

        return self.finish_auth(resp, conn)

    def finish_auth(
        self, orig_resp: Mapping[str, Any], conn: Connection
    ) -> Optional[Mapping[str, Any]]:
        conversation_id = orig_resp["conversationId"]
        token = self.get_current_token()
        conn.oidc_token_gen_id = self.token_gen_id
        bin_payload = Binary(bson.encode({"jwt": token}))
        cmd = SON(
            [
                ("saslContinue", 1),
                ("conversationId", conversation_id),
                ("payload", bin_payload),
            ]
        )
        resp = self.run_command(conn, cmd)
        assert resp is not None
        if not resp["done"]:
            raise OperationFailure("SASL conversation failed to complete.")
        return resp


def _authenticate_oidc(
    credentials: MongoCredential, conn: Connection, reauthenticate: bool
) -> Optional[Mapping[str, Any]]:
    """Authenticate using MONGODB-OIDC."""
    authenticator = _get_authenticator(credentials, conn.address)
    if reauthenticate:
        return authenticator.reauthenticate(conn)
    else:
        return authenticator.authenticate(conn)
