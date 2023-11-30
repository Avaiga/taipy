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

from ..exceptions.exceptions import InvalidEventOperation
from .event import _UNSUBMITTABLE_ENTITY_TYPES, EventEntityType, EventOperation


class _Topic:
    def __init__(
        self,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ):

        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = self.__preprocess_operation(operation, self.entity_type)
        self.attribute_name = self.__preprocess_attribute_name(attribute_name, self.operation)

    @classmethod
    def __preprocess_attribute_name(
        cls, attribute_name: Optional[str] = None, operation: Optional[EventOperation] = None
    ) -> Optional[str]:

        # if operation in _NO_ATTRIBUTE_NAME_OPERATIONS and attribute_name is not None:
        #     raise InvalidEventAttributeName
        return attribute_name

    @classmethod
    def __preprocess_operation(
        cls, operation: Optional[EventOperation] = None, entity_type: Optional[EventEntityType] = None
    ) -> Optional[EventOperation]:
        if (
            entity_type
            and operation
            and entity_type in _UNSUBMITTABLE_ENTITY_TYPES
            and operation == EventOperation.SUBMISSION
        ):
            raise InvalidEventOperation
        return operation

    def __hash__(self):
        return hash((self.entity_type, self.entity_id, self.operation, self.attribute_name))

    def __eq__(self, __value) -> bool:
        if (
            self.entity_type == __value.entity_type
            and self.entity_id == __value.entity_id
            and self.operation == __value.operation
            and self.attribute_name == __value.attribute_name
        ):
            return True
        return False
