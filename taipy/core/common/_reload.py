import functools


def get_manager(manager: str):
    from taipy.core.cycle.cycle_manager import CycleManager
    from taipy.core.data.data_manager import DataManager
    from taipy.core.job.job_manager import JobManager
    from taipy.core.pipeline.pipeline_manager import PipelineManager
    from taipy.core.scenario.scenario_manager import ScenarioManager
    from taipy.core.task.task_manager import TaskManager

    return {
        "scenario": ScenarioManager,
        "pipeline": PipelineManager,
        "data": DataManager,
        "cycle": CycleManager,
        "job": JobManager,
        "task": TaskManager,
    }[manager]


def reload(manager: str, obj):
    return get_manager(manager)._get(obj, obj)


def set_entity(manager: str, obj):
    # TODO: tp.set(obj)
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
