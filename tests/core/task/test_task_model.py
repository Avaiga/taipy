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

from taipy.config.common.scope import Scope
from taipy.core.data import InMemoryDataNode
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.task._task_model import _TaskModel


def test_none_properties_attribute_compatible():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["output_id"],
            "version": "latest",
            "skippable": False,
        }
    )
    assert len(model.properties) == 0


def test_skippable_compatibility_with_non_existing_output():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "owner_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["output_id"],
            "version": "latest",
            "skippable": False,
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_no_output():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "owner_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": [],
            "version": "latest",
            "skippable": False,
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_one_output():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.SCENARIO, id="dn_id"))

    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "owner_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id"],
            "version": "latest",
            "skippable": True,
        }
    )
    assert model.skippable


def test_skippable_compatibility_with_many_outputs():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.SCENARIO, id="dn_id"))
    manager._set(InMemoryDataNode("cfg_id_2", Scope.SCENARIO, id="dn_2_id"))
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "owner_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id", "dn_2_id"],
            "version": "latest",
            "skippable": True,
        }
    )
    assert model.skippable
