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

import functools

from ..notification import EventEntityType, EventOperation, _publish_event


@functools.lru_cache
def _get_manager(manager: str):
    from ..cycle._cycle_manager_factory import _CycleManagerFactory
    from ..data._data_manager_factory import _DataManagerFactory
    from ..job._job_manager_factory import _JobManagerFactory
    from ..pipeline._pipeline_manager_factory import _PipelineManagerFactory
    from ..scenario._scenario_manager_factory import _ScenarioManagerFactory
    from ..task._task_manager_factory import _TaskManagerFactory

    return {
        "scenario": _ScenarioManagerFactory._build_manager(),
        "pipeline": _PipelineManagerFactory._build_manager(),
        "data": _DataManagerFactory._build_manager(),
        "cycle": _CycleManagerFactory._build_manager(),
        "job": _JobManagerFactory._build_manager(),
        "task": _TaskManagerFactory._build_manager(),
    }[manager]


def _reload(manager: str, obj):
    return _get_manager(manager)._get(obj, obj)


def _self_setter(manager):
    def __set_entity(fct):
        @functools.wraps(fct)
        def _do_set_entity(self, *args, **kwargs):
            fct(self, *args, **kwargs)
            if not self._is_in_context:
                entity_manager = _get_manager(manager)
                entity_manager._set(self)
                _publish_event(entity_manager._EVENT_ENTITY_TYPE, self.id, EventOperation.UPDATE, fct.__name__)

        return _do_set_entity

    return __set_entity


def _self_reload(manager):
    def __reload(fct):
        @functools.wraps(fct)
        def _do_reload(self, *args, **kwargs):
            self = _reload(manager, self)
            return fct(self, *args, **kwargs)

        return _do_reload

    return __reload
