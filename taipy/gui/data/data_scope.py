from __future__ import annotations

import typing as t
import warnings
from types import SimpleNamespace

from flask import request


class _DataScopes:
    def __init__(self) -> None:
        self.__scopes: t.Dict[str, SimpleNamespace] = {}
        self.__scopes["global"] = SimpleNamespace()

    def get_scope(self) -> SimpleNamespace:
        # global context in case request is not registered or client_id is not available (such as in the context of running tests)
        if not request or (not hasattr(request, "sid") and "client_id" not in request.args.to_dict()):
            return self.__scopes["global"]
        if client_id := request.args.get("client_id"):
            return self.__scopes[client_id]
        if request.sid is None:  # type: ignore
            warnings.warn("Empty session id, using global scope instead")
            return self.__scopes["global"]
        if request.sid not in self.__scopes:  # type: ignore
            warnings.warn(
                f"session id {request.sid} not found in data scope. Taipy will automatically create a scope for this session id but you might have to reload your webpage"  # type: ignore
            )
            self.create_scope()
        return self.__scopes[request.sid]  # type: ignore

    def get_all_scopes(self) -> t.Dict[str, SimpleNamespace]:
        return self.__scopes

    def get_global_scope(self) -> SimpleNamespace:
        return self.__scopes["global"]

    def broadcast_data(self, name, value):
        if not hasattr(request, "sid"):
            for _, v in self.__scopes.items():
                if name in v:
                    setattr(v, name, value)

    def create_scope(self) -> None:
        if request.sid is None:  # type: ignore
            warnings.warn("Empty session id, might be due to unestablished WebSocket connection")
            return
        self.__scopes[request.sid] = SimpleNamespace()  # type: ignore

    def delete_scope(self) -> None:
        if request.sid is None:  # type: ignore
            warnings.warn("Empty session id, might be due to unestablished WebSocket connection")
            return
        if request.sid in self.__scopes:  # type: ignore
            del self.__scopes[request.sid]  # type: ignore
