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

from src.taipy.core.data import InMemoryDataNode
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.task._task_model import _TaskModel
from taipy.config.common.scope import Scope


def test_deprecated_owner_id():
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
        }
    )
    assert model.owner_id == "owner_id"


def test_override_deprecated_owner_id():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "parent_id",
            "owner_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["output_id"],
            "version": "latest",
        }
    )
    assert model.owner_id == "owner_id"


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
        }
    )
    assert len(model.properties) == 0


def test_skippable_compatibility_with_non_existing_output():
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
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_no_output():
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": [],
            "version": "latest",
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_one_cacheable_output():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id", properties={"cacheable": True}))

    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id"],
            "version": "latest",
        }
    )
    assert model.skippable


def test_skippable_compatibility_with_one_non_cacheable_output():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id", properties={"cacheable": False}))
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id"],
            "version": "latest",
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_one_non_cacheable_existing_output():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id"))
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id"],
            "version": "latest",
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_all_cacheable_outputs():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id", properties={"cacheable": True}))
    manager._set(InMemoryDataNode("cfg_id_2", Scope.PIPELINE, id="dn_2_id", properties={"cacheable": True}))
    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id", "dn_2_id"],
            "version": "latest",
        }
    )
    assert model.skippable


def test_skippable_compatibility_with_one_cacheable_output_over_two():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id", properties={"cacheable": True}))
    manager._set(InMemoryDataNode("cfg_id_2", Scope.PIPELINE, id="dn_2_id", properties={"cacheable": False}))

    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id", "dn_2_id"],
            "version": "latest",
        }
    )
    assert not model.skippable


def test_skippable_compatibility_with_one_cacheable_output_and_one_non_cacheable_existing():
    manager = _DataManagerFactory._build_manager()
    manager._set(InMemoryDataNode("cfg_id", Scope.PIPELINE, id="dn_id", properties={"cacheable": True}))
    manager._set(InMemoryDataNode("cfg_id_2", Scope.PIPELINE, id="dn_2_id"))

    model = _TaskModel.from_dict(
        {
            "id": "id",
            "config_id": "config_id",
            "parent_id": "owner_id",
            "parent_ids": ["parent_id"],
            "input_ids": ["input_id"],
            "function_name": "function_name",
            "function_module": "function_module",
            "output_ids": ["dn_id", "dn_2_id"],
            "version": "latest",
        }
    )
    assert not model.skippable
