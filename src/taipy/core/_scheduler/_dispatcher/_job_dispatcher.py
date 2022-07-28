# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from abc import abstractmethod
from typing import Any, List

from taipy import JobConfig
from taipy.config import Config
from taipy.config._toml_serializer import _TomlSerializer

from ...common.alias import JobId
from ...data._data_manager_factory import _DataManagerFactory
from ...data.data_node import DataNode
from ...exceptions.exceptions import DataNodeWritingError
from ...job._job_manager_factory import _JobManagerFactory
from ...job.job import Job
from ...task.task import Task


class _JobDispatcher:
    """Manages job dispatching (instances of `Job^` class) on executors."""

    def __init__(self):
        pass

    @abstractmethod
    def _can_execute(self) -> bool:
        """Returns True if the dispatcher have resources to execute a new job."""
        raise NotImplementedError

    @abstractmethod
    def _dispatch(self, job: Job):
        """
        Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        raise NotImplementedError

    @classmethod
    def _run_wrapped_function(cls, mode, config_as_string, job_id: JobId, task: Task):
        """
        Reads inputs, execute function, and write outputs.

        Parameters:
            mode: The job execution mode.
            config_as_string: The applied config passed as string to be reloaded iff the mode is `standalone`.
            job_id (JobId^): The id of the job.
            task (Task^): The task to be executed.
        Returns:
             True if the task needs to run. False otherwise.
        """
        try:
            if mode != JobConfig._DEVELOPMENT_MODE:
                Config._applied_config = _TomlSerializer()._deserialize(config_as_string)
            inputs: List[DataNode] = list(task.input.values())
            outputs: List[DataNode] = list(task.output.values())
            fct = task.function
            results = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, results, job_id)
        except Exception as e:
            return [e]

    @classmethod
    def __read_inputs(cls, inputs: List[DataNode]) -> List[Any]:
        data_manager = _DataManagerFactory._build_manager()
        return [data_manager._get(dn.id).read_or_raise() for dn in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataNode], results, job_id: JobId):
        data_manager = _DataManagerFactory._build_manager()
        try:
            if outputs:
                _results = cls.__extract_results(outputs, results)
                exceptions = []
                for res, dn in zip(_results, outputs):
                    try:
                        data_node = data_manager._get(dn.id)
                        data_node.write(res, job_id=job_id)
                        data_manager._set(data_node)
                    except Exception as e:
                        exceptions.append(DataNodeWritingError(f"Error writing in datanode id {dn.id}: {e}"))
                return exceptions
        except Exception as e:
            return [e]

    @classmethod
    def __extract_results(cls, outputs: List[DataNode], results: Any) -> List[Any]:
        _results: List[Any] = [results] if len(outputs) == 1 else results
        if len(_results) != len(outputs):
            raise DataNodeWritingError("Error: wrong number of result or task output")
        return _results

    @staticmethod
    def _update_status(job, exceptions):
        job.update_status(exceptions)
        _JobManagerFactory._build_manager()._set(job)
