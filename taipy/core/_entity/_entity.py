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

from typing import List

from .._entity._reload import _get_manager
from ..notification import Notifier


class _Entity:
    _ID_PREFIX: str
    _MANAGER_NAME: str
    _is_in_context = False
    _in_context_attributes_changed_collector: List

    def __enter__(self):
        self._is_in_context = True
        self._in_context_attributes_changed_collector = []
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # If multiple entities is in context, the last to enter will be the first to exit
        self._is_in_context = False
        if hasattr(self, "_properties"):
            for to_delete_key in self._properties._pending_deletions:
                self._properties.data.pop(to_delete_key, None)
            self._properties.data.update(self._properties._pending_changes)
        _get_manager(self._MANAGER_NAME)._set(self)

        for event in self._in_context_attributes_changed_collector:
            Notifier.publish(event)
        _get_manager(self._MANAGER_NAME)._set(self)
