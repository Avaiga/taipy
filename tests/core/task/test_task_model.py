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

from src.taipy.core.task._task_model import _TaskModel


def test_deprecated_properties():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["output_id"],
        }
    )
    assert model.owner_id == "owner_id"


def test_override_deprecated_properties():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "parent_id",
            "owner_id": "owner_id",
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["output_id"],
        }
    )
    assert model.owner_id == "owner_id"
