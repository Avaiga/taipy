import logging
import pathlib
from collections import defaultdict

from taipy.common import utils
from taipy.common.alias import Dag, TaskId
from taipy.config.config import Config
from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.repository import FileSystemRepository
from taipy.task.task_manager import TaskManager


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
            pipeline.config_name,
            pipeline.properties,
            Dag(dict(datanode_task_edges)),
            Dag(dict(task_datanode_edges)),
            utils.fcts_to_dict(pipeline.subscribers),
        )

    def from_model(self, model: PipelineModel) -> Pipeline:
        try:
            tasks = self.__to_tasks(model.task_datanode_edges.keys())
            pipeline = Pipeline(model.name, model.properties, tasks, model.id, model.parent_id)
            pipeline.subscribers = {utils.load_fct(it["fct_module"], it["fct_name"]) for it in model.subscribers}
            return pipeline
        except NonExistingTask as err:
            logging.error(err.message)
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(model.id)
            logging.error(pipeline_err.message)
            raise pipeline_err

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config().storage_folder)  # type: ignore

    @staticmethod
    def __to_tasks(task_ids):
        return [TaskManager().get(TaskId(i)) for i in task_ids]
