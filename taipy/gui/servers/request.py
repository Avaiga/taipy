# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


from typing import Any, Optional

from flask.ctx import _AppCtxGlobals


class _BaseRequestAccessor:
    _request_meta: _AppCtxGlobals = _AppCtxGlobals()

    def args(self, to_dict=False) -> Any:
        return {}

    def arg(self, key, default=None) -> Any:
        return default

    def form(self) -> Any:
        return {}

    def files(self) -> Any:
        return {}

    def cookies(self) -> Any:
        return {}

    def sid(self) -> Any:
        return None

    def set_sid(self, incoming_sid: Optional[str]) -> None:
        pass

    def get_request(self) -> Any:
        return None

    def get_request_meta(self) -> Any:
        return self._request_meta

    def has_request_context(self) -> bool:
        return False
