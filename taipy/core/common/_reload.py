import functools


@functools.lru_cache
def _get_manager(manager: str):
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


def _reload(manager: str, obj):
    return _get_manager(manager)._get(obj, obj)


def _set_entity(manager: str, obj):
    _get_manager(manager)._set(obj)


def _self_setter(manager):
    def __set_entity(fct):
        @functools.wraps(fct)
        def _do_set_entity(self, *args, **kwargs):
            fct(self, *args, **kwargs)
            if not self._is_in_context:
                _set_entity(manager, self)

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
