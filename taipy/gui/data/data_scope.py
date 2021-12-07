from __future__ import annotations

import typing as t
import warnings
from types import SimpleNamespace

from flask import request


class _DataScopes:
    def __init__(self) -> None:
        self._scopes: t.Dict[str, SimpleNamespace] = {}

    def get_scope(self) -> SimpleNamespace:
        if request.sid is None:
            raise RuntimeError("Empty session id, might be due to unestablished WebSocket connection")
        if request.sid not in self._scopes:
            warnings.warn(
                f"session id {request.sid} not found in data scope. Taipy will automatically create a scope for this session id but you might have to reload your webpage"
            )
            self.create_scope()
        return self._scopes[request.sid]

    def create_scope(self) -> None:
        if request.sid is None:
            raise RuntimeError("Empty session id, might be due to unestablished WebSocket connection")
        self._scopes[request.sid] = SimpleNamespace()
        print("New data scope created for session id " + request.sid)

    def delete_scope(self) -> None:
        if request.sid is None:
            raise RuntimeError("Empty session id, might be due to unestablished WebSocket connection")
        if request.sid in self._scopes:
            del self._scopes[request.sid]
            print("Data scope deleted for session id " + request.sid)
