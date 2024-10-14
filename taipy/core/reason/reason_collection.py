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

from .reason import Reason


class ReasonCollection:
    """Class used to store all the reasons to explain why some Taipy operations are not allowed.

    Because Taipy applications are natively multiuser, asynchronous, and dynamic,
    some functions might not be called in some specific contexts. You can protect
    such calls by calling other methods that return a `ReasonCollection`. It acts like a
    boolean: True if the operation can be performed and False otherwise.
    If the action cannot be performed, the ReasonCollection holds all the individual reasons as
    a list of `Reason` objects. Each `Reason` explains why the operation cannot be performed.
    """

    def __init__(self) -> None:
        self._reasons: Dict[str, Set[Reason]] = {}

    def _add_reason(self, entity_id: str, reason: Reason) -> "ReasonCollection":
        if entity_id not in self._reasons:
            self._reasons[entity_id] = set()
        self._reasons[entity_id].add(reason)
        return self

    def _remove_reason(self, entity_id: str, reason: Reason) -> "ReasonCollection":
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
        """Retrieves a collection of reasons as a string that explains why the action cannot be performed.

        Returns:
            A string that contains all the reasons why the action cannot be performed.
        """
        if self._reasons:
            return "; ".join("; ".join([str(reason) for reason in reasons]) for reasons in self._reasons.values()) + "."
        return ""
