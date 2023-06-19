# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from collections import UserDict

from ..notification import _ENTITY_TO_EVENT_ENTITY_TYPE, EventOperation, _publish_event


class _Properties(UserDict):
    def __init__(self, entity_owner, **kwargs):
        super().__init__(**kwargs)
        self._entity_owner = entity_owner
        self._current_in_context_entity_owner = None

    def __setitem__(self, key, value):
        super(_Properties, self).__setitem__(key, value)
        from ... import core as tp

        if hasattr(self, "_entity_owner") and getattr(self, "_entity_owner"):
            to_publish_event_parameters = [
                _ENTITY_TO_EVENT_ENTITY_TYPE[self._entity_owner._MANAGER_NAME],
                self._entity_owner.id,
                EventOperation.UPDATE,
                key,
            ]
            if not self._entity_owner._is_in_context:
                self._entity_owner._properties = self
                tp.set(self._entity_owner)
                _publish_event(*to_publish_event_parameters)
            else:
                self._entity_owner._in_context_attributes_changed_collector.append(to_publish_event_parameters)
        elif hasattr(self, "_current_in_context_entity_owner"):
            to_publish_event_parameters = [
                _ENTITY_TO_EVENT_ENTITY_TYPE[self._current_in_context_entity_owner._MANAGER_NAME],
                self._current_in_context_entity_owner.id,
                EventOperation.UPDATE,
                key,
            ]
            self._current_in_context_entity_owner._properties[key] = value
            self._current_in_context_entity_owner._in_context_attributes_changed_collector.append(
                to_publish_event_parameters
            )

    def __getitem__(self, key):
        from taipy.config.common._template_handler import _TemplateHandler as _tpl

        return _tpl._replace_templates(super(_Properties, self).__getitem__(key))
