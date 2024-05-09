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


class Reason:
    def __init__(self, entity_id: str) -> None:
        self.entity_id: str = entity_id
        self.reasons: Dict[str, Set[str]] = {}

    def _add_reason(self, entity_id: str, reason: str) -> None:
        if entity_id not in self.reasons:
            self.reasons[entity_id] = set()
        self.reasons[entity_id].add(reason)

    def _remove_reason(self, entity_id: str, reason: str) -> None:
        if entity_id in self.reasons and reason in self.reasons[entity_id]:
            self.reasons[entity_id].remove(reason)
            if len(self.reasons[entity_id]) == 0:
                del self.reasons[entity_id]

    def _entity_id_exists_in_reason(self, entity_id: str) -> bool:
        return entity_id in self.reasons

    def __bool__(self) -> bool:
        return len(self.reasons) == 0
