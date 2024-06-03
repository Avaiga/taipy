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

from typing import Dict, Set


class Reasons:
    def __init__(self, entity_id: str) -> None:
        self.entity_id: str = entity_id
        self._reasons: Dict[str, Set[str]] = {}

    def _add_reason(self, entity_id: str, reason: str) -> "Reasons":
        if entity_id not in self._reasons:
            self._reasons[entity_id] = set()
        self._reasons[entity_id].add(reason)
        return self

    def _remove_reason(self, entity_id: str, reason: str) -> "Reasons":
        if entity_id in self._reasons and reason in self._reasons[entity_id]:
            self._reasons[entity_id].remove(reason)
            if len(self._reasons[entity_id]) == 0:
                del self._reasons[entity_id]
        return self

    def _entity_id_exists_in_reason(self, entity_id: str) -> bool:
        return entity_id in self._reasons

    def __bool__(self) -> bool:
        return len(self._reasons) == 0

    @property
    def reasons(self) -> str:
        return "; ".join("; ".join(reason) for reason in self._reasons.values()) + "." if self._reasons else ""
