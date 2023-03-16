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

from datetime import datetime
from typing import Optional

from ..common._repr_enum import _ReprEnum


class EventOperation(_ReprEnum):
    CREATION = 1
    UPDATE = 2
    DELETION = 3
    # SUBMISSION = 4


class EventEntityType(_ReprEnum):
    CYCLE = 1
    SCENARIO = 2
    PIPELINE = 3
    TASK = 4
    DATA_NODE = 5
    JOB = 6


class Event:
    def __init__(
        self,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ):
        self.creation_date = datetime.now()
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = operation
        self.attribute_name = attribute_name
