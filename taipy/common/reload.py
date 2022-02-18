import functools


def reload(manager: str, obj):
    from taipy.data.data_manager import DataManager
    from taipy.pipeline.pipeline_manager import PipelineManager
    from taipy.scenario.scenario_manager import ScenarioManager

    manager_cls = {"scenario": ScenarioManager, "pipeline": PipelineManager, "data": DataManager}[manager]

    return manager_cls.get(obj, obj)  # type: ignore


def self_reload(manager):
    def _reload(fct):
        @functools.wraps(fct)
        def __reload(self, *args, **kwargs):
            self = reload(manager, self)
            return fct(self, *args, **kwargs)

        return __reload

    return _reload
