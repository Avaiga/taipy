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
from queue import Queue

from .topic import Topic


class Registration:
    def __init__(self, register_id, entity_type, entity_id, operation, attribute_name):
        self.register_id = register_id
        self.queue = Queue()
        self.topic = Topic(entity_type, entity_id, operation, attribute_name)
