from __future__ import annotations

import typing as t
import warnings
from types import SimpleNamespace

from flask import request


class _DataScopes:
    def __init__(self) -> None:
        self._scopes: t.Dict[str, SimpleNamespace] = {}
        self._scopes["global"] = SimpleNamespace()

    def get_scope(self) -> SimpleNamespace:
        # global context in case request is not registered of client_id is not available (such as in the context of running tests)
        if not request or (not hasattr(request, "sid") and "client_id" not in request.args.to_dict()):
            return self._scopes["global"]
        if client_id := request.args.get("client_id"):
            return self._scopes[client_id]
        if request.sid is None:  # type: ignore
            warnings.warn("Empty session id, using global scope instead")
            return self._scopes["global"]
        if request.sid not in self._scopes:  # type: ignore
            warnings.warn(
                f"session id {request.sid} not found in data scope. Taipy will automatically create a scope for this session id but you might have to reload your webpage"  # type: ignore
            )
            self.create_scope()
        return self._scopes[request.sid]  # type: ignore

    def create_scope(self) -> None:
        if request.sid is None:  # type: ignore
            raise RuntimeError("Empty session id, might be due to unestablished WebSocket connection")
        self._scopes[request.sid] = SimpleNamespace()  # type: ignore
        print("New data scope created for session id " + request.sid)  # type: ignore

    def delete_scope(self) -> None:
        if request.sid is None:  # type: ignore
            raise RuntimeError("Empty session id, might be due to unestablished WebSocket connection")
        if request.sid in self._scopes:  # type: ignore
            del self._scopes[request.sid]  # type: ignore
            print("Data scope deleted for session id " + request.sid)  # type: ignore
