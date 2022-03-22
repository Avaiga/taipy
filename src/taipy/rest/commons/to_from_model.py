from taipy.core.cycle._cycle_repository import _CycleRepository
from taipy.core.data._data_repository import _DataRepository
from taipy.core.pipeline._pipeline_repository import _PipelineRepository
from taipy.core.scenario._scenario_repository import _ScenarioRepository
from taipy.core.task._task_repository import _TaskRepository

repositories = {
    "scenario": _ScenarioRepository,
    "pipeline": _PipelineRepository,
    "task": _TaskRepository,
    "data": _DataRepository,
    "cycle": _CycleRepository,
}


def to_model(repository, entity, **kwargs):
    return repositories[repository](**kwargs)._to_model(entity)
