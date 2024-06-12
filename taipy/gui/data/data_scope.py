# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import typing as t
from types import SimpleNamespace

from .._warnings import _warn

if t.TYPE_CHECKING:
    from ..gui import Gui


class _DataScopes:
    _GLOBAL_ID = "global"
    _META_PRE_RENDER = "pre_render"
    _DEFAULT_METADATA = {_META_PRE_RENDER: False}

    def __init__(self, gui: "Gui") -> None:
        self.__gui = gui
        self.__scopes: t.Dict[str, SimpleNamespace] = {_DataScopes._GLOBAL_ID: SimpleNamespace()}
        # { scope_name: { metadata: value } }
        self.__scopes_metadata: t.Dict[str, t.Dict[str, t.Any]] = {
            _DataScopes._GLOBAL_ID: _DataScopes._DEFAULT_METADATA.copy()
        }
        self.__single_client = True

    def set_single_client(self, value: bool) -> None:
        self.__single_client = value

    def is_single_client(self) -> bool:
        return self.__single_client

    def get_scope(self, client_id: t.Optional[str]) -> t.Tuple[SimpleNamespace, t.Dict[str, str]]:
        if self.__single_client:
            return self.__scopes[_DataScopes._GLOBAL_ID], self.__scopes_metadata[_DataScopes._GLOBAL_ID]
        # global context in case request is not registered or client_id is not
        # available (such as in the context of running tests)
        if not client_id:
            _warn("Empty session id, using global scope instead.")
            return self.__scopes[_DataScopes._GLOBAL_ID], self.__scopes_metadata[_DataScopes._GLOBAL_ID]
        if client_id not in self.__scopes:
            _warn(
                f"Session id {client_id} not found in data scope. Taipy will automatically create a scope for this session id but you may have to reload your page."  # noqa: E501
            )
            self.create_scope(client_id)
        return self.__scopes[client_id], self.__scopes_metadata[client_id]

    def get_all_scopes(self) -> t.Dict[str, SimpleNamespace]:
        return self.__scopes

    def create_scope(self, id: str) -> None:
        if self.__single_client:
            return
        if id is None:
            _warn("Empty session id, might be due to unestablished WebSocket connection.")
            return
        if id not in self.__scopes:
            self.__scopes[id] = SimpleNamespace()
            self.__scopes_metadata[id] = _DataScopes._DEFAULT_METADATA.copy()
            # Propagate shared variables to the new scope from the global scope
            for var in self.__gui._get_shared_variables():
                if hasattr(self.__scopes[_DataScopes._GLOBAL_ID], var):
                    setattr(self.__scopes[id], var, getattr(self.__scopes[_DataScopes._GLOBAL_ID], var, None))

    def delete_scope(self, id: str) -> None:  # pragma: no cover
        if self.__single_client:
            return
        if id is None:
            _warn("Empty session id, might be due to unestablished WebSocket connection.")
            return
        if id in self.__scopes:
            del self.__scopes[id]
            del self.__scopes_metadata[id]
