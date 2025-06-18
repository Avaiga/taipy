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

import functools
import threading
from typing import Dict, Type

from ...common._modules import EnterpriseEdition
from .._manager._manager import _Manager
from ..common._utils import _load_fct
from ..notification import EventOperation, Notifier, _make_event


class _Reloader:
    """The _Reloader singleton class"""

    _instance = None
    _lock = threading.RLock()
    _managers: Dict[str, Type[_Manager]] = {}

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not isinstance(cls._instance, cls):
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance._no_reload_context = False  # Initialize once
                cls._instance._context_depth = 0  # Track nested `with` usage
            cls._managers = cls._build_managers()
        return cls._instance

    def _reload(self, manager: str, obj):
        if self._no_reload_context:
            return obj

        entity = self._get_manager(manager)._get(obj, obj)
        if obj._is_in_context and hasattr(entity, "_properties"):
            if obj._properties._pending_changes:
                entity._properties._pending_changes = obj._properties._pending_changes
            if obj._properties._pending_deletions:
                entity._properties._pending_deletions = obj._properties._pending_deletions
            entity._properties._entity_owner = obj
        return entity

    def __enter__(self):
        with self._lock:
            self._context_depth += 1
            self._no_reload_context = True
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with self._lock:
            self._context_depth -= 1
            if self._context_depth == 0:
                self._no_reload_context = False

    @classmethod
    @functools.lru_cache
    def _build_managers(cls) -> Dict[str, Type[_Manager]]:
        from ..cycle._cycle_manager_factory import _CycleManagerFactory
        from ..data._data_manager_factory import _DataManagerFactory
        from ..job._job_manager_factory import _JobManagerFactory
        from ..scenario._scenario_manager_factory import _ScenarioManagerFactory
        from ..sequence._sequence_manager_factory import _SequenceManagerFactory
        from ..submission._submission_manager_factory import _SubmissionManagerFactory
        from ..task._task_manager_factory import _TaskManagerFactory

        managers: Dict[str, Type[_Manager]] = {
            "scenario": _ScenarioManagerFactory._build_manager(),
            "sequence": _SequenceManagerFactory._build_manager(),
            "data": _DataManagerFactory._build_manager(),
            "cycle": _CycleManagerFactory._build_manager(),
            "job": _JobManagerFactory._build_manager(),
            "task": _TaskManagerFactory._build_manager(),
            "submission": _SubmissionManagerFactory._build_manager(),
        }

        if EnterpriseEdition._is_installed():
            _build_enterprise_managers = _load_fct(
                EnterpriseEdition._CORE_MODULE_PATH + "._entity.utils", "_build_enterprise_managers"
            )
            managers.update(_build_enterprise_managers())

        return managers

    @classmethod
    @functools.lru_cache
    def _get_manager(cls, manager: str) -> Type[_Manager]:
        return cls._managers[manager]


def _self_reload(manager: str):
    def __reload(fct):
        @functools.wraps(fct)
        def _do_reload(self, *args, **kwargs):
            self = _Reloader()._reload(manager, self)
            return fct(self, *args, **kwargs)

        return _do_reload

    return __reload


def _self_setter(manager):
    def __update_entity(fct):
        @functools.wraps(fct)
        def _do_update_entity(self, *args, **kwargs):
            fct(self, *args, **kwargs)
            value = args[0] if len(args) == 1 else args
            event = _make_event(
                self,
                EventOperation.UPDATE,
                attribute_name=fct.__name__,
                attribute_value=value,
            )
            if not self._is_in_context:
                entity = _Reloader()._reload(manager, self)
                fct(entity, *args, **kwargs)
                _Reloader._get_manager(manager)._update(entity)
                Notifier.publish(event)
            else:
                self._in_context_attributes_changed_collector.append(event)

        return _do_update_entity

    return __update_entity
