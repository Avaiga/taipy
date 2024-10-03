# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Any, List

from taipy.common.config import Config
from taipy.common.config._serializer._toml_serializer import _TomlSerializer
from taipy.common.logger._taipy_logger import _TaipyLogger

from ...data._data_manager_factory import _DataManagerFactory
from ...data.data_node import DataNode
from ...exceptions import DataNodeWritingError
from ...job.job_id import JobId
from ...task.task import Task

logger = _TaipyLogger._get_logger()


class _TaskFunctionWrapper:
    """Wrapper around task function."""

    def __init__(self, job_id: JobId, task: Task):
        self.job_id = job_id
        self.task = task

    def __call__(self, **kwargs):
        """Make this object callable as a function. Actually calls `execute`."""
        return self.execute(**kwargs)

    def execute(self, **kwargs):
        """Execute the wrapped function. If `config_as_string` is given, then it will be reapplied to the config."""
        try:
            if config_as_string := kwargs.pop("config_as_string", None):
                Config._applied_config._update(_TomlSerializer()._deserialize(config_as_string))
                Config.block_update()

            inputs = list(self.task.input.values())
            outputs = list(self.task.output.values())

            arguments = self._read_inputs(inputs)
            results = self._execute_fct(arguments)
            return self._write_data(outputs, results, self.job_id)
        except Exception as e:
            logger.error("Error during task function execution!", exc_info=1)
            return [e]

    def _read_inputs(self, inputs: List[DataNode]) -> List[Any]:
        data_manager = _DataManagerFactory._build_manager()
        return [data_manager._get(dn.id).read_or_raise() for dn in inputs]

    def _write_data(self, outputs: List[DataNode], results, job_id: JobId):
        data_manager = _DataManagerFactory._build_manager()
        try:
            if outputs:
                _results = self._extract_results(outputs, results)
                exceptions = []
                for res, dn in zip(_results, outputs):
                    try:
                        data_node = data_manager._get(dn.id)
                        data_node.write(res, job_id=job_id)
                    except Exception as e:
                        logger.error("Error during write", exc_info=1)
                        exceptions.append(DataNodeWritingError(f"Error writing in datanode id {dn.id}: {e}"))
                return exceptions
        except Exception as e:
            return [e]

    def _execute_fct(self, arguments: List[Any]) -> Any:
        return self.task.function(*arguments)

    def _extract_results(self, outputs: List[DataNode], results: Any) -> List[Any]:
        _results: List[Any] = [results] if len(outputs) == 1 else results
        if len(_results) != len(outputs):
            raise DataNodeWritingError("Error: wrong number of result or task output")
        return _results
