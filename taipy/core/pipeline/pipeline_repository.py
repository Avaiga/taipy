import pathlib
from collections import defaultdict

from taipy.core.common import _utils
from taipy.core.config.config import Config
from taipy.core.exceptions.pipeline import NonExistingPipeline
from taipy.core.exceptions.task import NonExistingTask
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_model import PipelineModel
from taipy.core.repository import FileSystemRepository
from taipy.core.task.task_manager import TaskManager


class PipelineRepository(FileSystemRepository[PipelineModel, Pipeline]):
    def __init__(self):
        super().__init__(model=PipelineModel, dir_name="pipelines")

    def to_model(self, pipeline: Pipeline) -> PipelineModel:
        datanode_task_edges = defaultdict(list)
        task_datanode_edges = defaultdict(list)
        for task in pipeline.tasks.values():
            for predecessor in task.input.values():
                datanode_task_edges[str(predecessor.id)].append(str(task.id))
            for successor in task.output.values():
                task_datanode_edges[str(task.id)].append(str(successor.id))
        return PipelineModel(
            pipeline.id,
            pipeline.parent_id,
            pipeline.config_id,
            pipeline._properties.data,
            [task.id for task in pipeline.tasks.values()],
            _utils._fcts_to_dict(pipeline._subscribers),
        )

    def from_model(self, model: PipelineModel) -> Pipeline:
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
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __to_tasks(task_ids):
        tasks = []
        for _id in task_ids:
            if task := TaskManager._get(_id):
                tasks.append(task)
            else:
                raise NonExistingTask(_id)
        return tasks
