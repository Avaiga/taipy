import pathlib
from collections import defaultdict

from taipy.core._repository import _FileSystemRepository
from taipy.core.common import _utils
from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import NonExistingPipeline, NonExistingTask
from taipy.core.pipeline._pipeline_model import _PipelineModel
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task._task_manager import _TaskManager


class _PipelineRepository(_FileSystemRepository[_PipelineModel, Pipeline]):
    def __init__(self):
        super().__init__(model=_PipelineModel, dir_name="pipelines")

    def _to_model(self, pipeline: Pipeline) -> _PipelineModel:
        datanode_task_edges = defaultdict(list)
        task_datanode_edges = defaultdict(list)
        for task in pipeline._tasks.values():
            for predecessor in task.input.values():
                datanode_task_edges[str(predecessor.id)].append(str(task.id))
            for successor in task.output.values():
                task_datanode_edges[str(task.id)].append(str(successor.id))
        return _PipelineModel(
            pipeline.id,
            pipeline._parent_id,
            pipeline._config_id,
            pipeline._properties.data,
            [task.id for task in pipeline._tasks.values()],
            _utils._fcts_to_dict(pipeline._subscribers),
        )

    def _from_model(self, model: _PipelineModel) -> Pipeline:
        try:
            tasks = self.__to_tasks(model.tasks)
            pipeline = Pipeline(
                model.config_id,
                model.properties,
                tasks,
                model.id,
                model.parent_id,
                {_utils._load_fct(it["fct_module"], it["fct_name"]) for it in model.subscribers},
            )
            return pipeline
        except NonExistingTask as err:
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(model.id)
            raise pipeline_err

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __to_tasks(task_ids):
        tasks = []
        for _id in task_ids:
            if task := _TaskManager._get(_id):
                tasks.append(task)
            else:
                raise NonExistingTask(_id)
        return tasks
