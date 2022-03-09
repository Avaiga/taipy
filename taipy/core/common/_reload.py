import functools


def reload(manager: str, obj):
    from taipy.core.data._data_manager import _DataManager
    from taipy.core.pipeline._pipeline_manager import _PipelineManager
    from taipy.core.scenario._scenario_manager import _ScenarioManager

    manager_cls = {"scenario": _ScenarioManager, "pipeline": _PipelineManager, "data": _DataManager}[manager]

    return manager_cls._get(obj, obj)  # type: ignore


def self_reload(manager):
    def _reload(fct):
        @functools.wraps(fct)
        def __reload(self, *args, **kwargs):
            self = reload(manager, self)
            return fct(self, *args, **kwargs)

        return __reload

    return _reload
