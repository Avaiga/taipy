import functools


def get_manager(manager: str):
    from taipy.core.cycle._cycle_manager import _CycleManager
    from taipy.core.data._data_manager import _DataManager
    from taipy.core.job._job_manager import _JobManager
    from taipy.core.pipeline._pipeline_manager import _PipelineManager
    from taipy.core.scenario._scenario_manager import _ScenarioManager
    from taipy.core.task._task_manager import _TaskManager

    return {
        "scenario": _ScenarioManager,
        "pipeline": _PipelineManager,
        "data": _DataManager,
        "cycle": _CycleManager,
        "job": _JobManager,
        "task": _TaskManager,
    }[manager]


def reload(manager: str, obj):
    return get_manager(manager)._get(obj, obj)


def set_entity(manager: str, obj):
    get_manager(manager)._set(obj)


def self_setter(manager):
    def _set_entity(fct):
        @functools.wraps(fct)
        def __set_entity(self, *args, **kwargs):
            fct(self, *args, **kwargs)
            if not self._is_in_context:
                set_entity(manager, self)

        return __set_entity

    return _set_entity


def self_reload(manager):
    def _reload(fct):
        @functools.wraps(fct)
        def __reload(self, *args, **kwargs):
            self = reload(manager, self)
            return fct(self, *args, **kwargs)

        return __reload

    return _reload
