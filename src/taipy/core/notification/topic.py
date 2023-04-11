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

from typing import Optional

from ..cycle.cycle import Cycle
from ..data.data_node import DataNode
from ..exceptions.exceptions import InvalidEntityId, InvalidEntityType
from ..job.job import Job
from ..pipeline.pipeline import Pipeline
from ..scenario.scenario import Scenario
from ..task.task import Task
from .event import Event, EventEntityType


class Topic:

    __ENTITY_TYPE_PREFIXES = {
        Cycle._ID_PREFIX: EventEntityType.CYCLE,
        Scenario._ID_PREFIX: EventEntityType.SCENARIO,
        Pipeline._ID_PREFIX: EventEntityType.PIPELINE,
        Task._ID_PREFIX: EventEntityType.TASK,
        DataNode._ID_PREFIX: EventEntityType.DATA_NODE,
        Job._ID_PREFIX: EventEntityType.JOB,
    }

    def __init__(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        operation: Optional[str] = None,
        attribute_name: Optional[str] = None,
    ):

        self.entity_type, self.entity_id = self.__preprocess_entity_type_and_entity_id(entity_type, entity_id)
        self.operation = operation
        self.attribute_name = attribute_name

    def __hash__(self):
        return (self.entity_type, self.entity_id, self.operation, self.attribute_name)

    @classmethod
    def __preprocess_entity_type_and_entity_id(cls, entity_type: Optional[str], entity_id: Optional[str]):
        if entity_type and entity_id:
            tmp_entity_type = cls.__get_entity_type_from_id(entity_id)
            if tmp_entity_type != entity_type:
                raise InvalidEntityType
            entity_type = tmp_entity_type
        else:
            if entity_type and entity_type not in cls.__ENTITY_TYPE_PREFIXES:
                raise InvalidEntityType
            if entity_id:
                entity_type = cls.__get_entity_type_from_id(entity_id)

        return entity_type, entity_id

    @classmethod
    def __get_entity_type_from_id(cls, entity_id: str):
        for entity_prefix, event_entity_type in cls.__ENTITY_TYPE_PREFIXES.items():
            if entity_id.startswith(entity_prefix):
                return event_entity_type
        raise InvalidEntityId

    # def __preprocess_attribute_name(self):
    #     if self.operation == EventOperation.CREATION/DELETION and self.attribute_name is not None:
    #         throw error?

    # def __preprocess_operation(self):
    #     if self.entity_type == EventEntityType.CYCLE and self.operation == EventOperation.SUBMISSION:
    #         throw error?
