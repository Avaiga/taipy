# Copyright 2023 Avaiga Private Limited
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

from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.config import Config

from ...data._data_manager_factory import _DataManagerFactory
from ...data.data_node import DataNode
from ...exceptions import DataNodeWritingError
from ...job.job_id import JobId
from ...task.task import Task


class _TaskFunctionWrapper:
    @classmethod
    def _wrapped_function_with_config_load(cls, config_as_string, job_id: JobId, task: Task):
        Config._applied_config._update(_TomlSerializer()._deserialize(config_as_string))
        Config.block_update()
        return cls._wrapped_function(job_id, task)

    @classmethod
    def _wrapped_function(cls, job_id: JobId, task: Task):
        try:
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
