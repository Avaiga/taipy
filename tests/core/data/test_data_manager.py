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
import os
import pathlib

import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core._version._version_manager import _VersionManager
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.exceptions.exceptions import InvalidDataNodeType, ModelNotFound
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)


class TestDataManager:
    def test_create_data_node_and_modify_properties_does_not_modify_config(self):
        dn_config = Config.configure_data_node(id="name", foo="bar")
        dn = _DataManager._create_and_set(dn_config, None, None)
        assert dn_config.properties.get("foo") == "bar"
        assert dn_config.properties.get("baz") is None

        dn.properties["baz"] = "qux"
        _DataManager._set(dn)
        assert dn_config.properties.get("foo") == "bar"
        assert dn_config.properties.get("baz") is None
        assert dn.properties.get("foo") == "bar"
        assert dn.properties.get("baz") == "qux"

    def test_create_data_node_with_name_provided(self):
        dn_config = Config.configure_data_node(id="dn", foo="bar", name="acb")
        dn = _DataManager._create_and_set(dn_config, None, None)
        assert dn.name == "acb"

    def test_create_and_get_csv_data_node(self):
        # Test we can instantiate a CsvDataNode from DataNodeConfig with :
        # - a csv type
        # - a default scenario scope
        # - No owner_id
        csv_dn_config = Config.configure_data_node(id="foo", storage_type="csv", path="bar", has_header=True)
        csv_dn = _DataManager._create_and_set(csv_dn_config, None, None)

        assert isinstance(csv_dn, CSVDataNode)
        assert isinstance(_DataManager._get(csv_dn.id), CSVDataNode)

        assert _DataManager._exists(csv_dn.id)
        assert _DataManager._get(csv_dn.id) is not None
        assert _DataManager._get(csv_dn.id).id == csv_dn.id
        assert _DataManager._get(csv_dn.id).config_id == "foo"
        assert _DataManager._get(csv_dn.id).config_id == csv_dn.config_id
        assert _DataManager._get(csv_dn.id).scope == Scope.SCENARIO
        assert _DataManager._get(csv_dn.id).scope == csv_dn.scope
        assert _DataManager._get(csv_dn.id).owner_id is None
        assert _DataManager._get(csv_dn.id).owner_id == csv_dn.owner_id
        assert _DataManager._get(csv_dn.id).parent_ids == set()
        assert _DataManager._get(csv_dn.id).parent_ids == csv_dn.parent_ids
        assert _DataManager._get(csv_dn.id).last_edit_date is None
        assert _DataManager._get(csv_dn.id).last_edit_date == csv_dn.last_edit_date
        assert _DataManager._get(csv_dn.id).job_ids == []
        assert _DataManager._get(csv_dn.id).job_ids == csv_dn.job_ids
        assert not _DataManager._get(csv_dn.id).is_ready_for_reading
        assert _DataManager._get(csv_dn.id).is_ready_for_reading == csv_dn.is_ready_for_reading
        assert len(_DataManager._get(csv_dn.id).properties) == 4
        assert _DataManager._get(csv_dn.id).properties.get("path") == "bar"
        assert _DataManager._get(csv_dn.id).properties.get("encoding") == "utf-8"
        assert _DataManager._get(csv_dn.id).properties.get("has_header") is True
        assert _DataManager._get(csv_dn.id).properties.get("exposed_type") == "pandas"
        assert _DataManager._get(csv_dn.id).properties == csv_dn.properties
        assert _DataManager._get(csv_dn.id).edit_in_progress is False
        assert _DataManager._get(csv_dn.id)._editor_id is None
        assert _DataManager._get(csv_dn.id)._editor_expiration_date is None

        assert _DataManager._get(csv_dn) is not None
        assert _DataManager._get(csv_dn).id == csv_dn.id
        assert _DataManager._get(csv_dn).config_id == "foo"
        assert _DataManager._get(csv_dn).config_id == csv_dn.config_id
        assert _DataManager._get(csv_dn).scope == Scope.SCENARIO
        assert _DataManager._get(csv_dn).scope == csv_dn.scope
        assert _DataManager._get(csv_dn).owner_id is None
        assert _DataManager._get(csv_dn).owner_id == csv_dn.owner_id
        assert _DataManager._get(csv_dn).parent_ids == set()
        assert _DataManager._get(csv_dn).parent_ids == csv_dn.parent_ids
        assert _DataManager._get(csv_dn).last_edit_date is None
        assert _DataManager._get(csv_dn).last_edit_date == csv_dn.last_edit_date
        assert _DataManager._get(csv_dn).job_ids == []
        assert _DataManager._get(csv_dn).job_ids == csv_dn.job_ids
        assert not _DataManager._get(csv_dn).is_ready_for_reading
        assert _DataManager._get(csv_dn).is_ready_for_reading == csv_dn.is_ready_for_reading
        assert len(_DataManager._get(csv_dn).properties) == 4
        assert _DataManager._get(csv_dn).properties.get("path") == "bar"
        assert _DataManager._get(csv_dn).properties.get("encoding") == "utf-8"
        assert _DataManager._get(csv_dn).properties.get("has_header") is True
        assert _DataManager._get(csv_dn.id).properties.get("exposed_type") == "pandas"
        assert _DataManager._get(csv_dn).properties == csv_dn.properties
        assert _DataManager._get(csv_dn.id).edit_in_progress is False
        assert _DataManager._get(csv_dn.id)._editor_id is None
        assert _DataManager._get(csv_dn.id)._editor_expiration_date is None

    def test_edit_and_get_data_node(self):
        config = Config.configure_pickle_data_node(id="foo")
        dn = _DataManager._create_and_set(config, None, None)

        assert _DataManager._get(dn.id).last_edit_date is None
        assert len(_DataManager._get(dn.id).properties) == 1
        assert _DataManager._get(dn.id).properties.get("is_generated")
        assert not _DataManager._get(dn.id).edit_in_progress
        assert _DataManager._get(dn.id)._editor_id is None
        assert _DataManager._get(dn.id)._editor_expiration_date is None

        dn.lock_edit("foo")

        assert _DataManager._get(dn.id).last_edit_date is None
        assert len(_DataManager._get(dn.id).properties) == 1
        assert _DataManager._get(dn.id).properties.get("is_generated")
        assert _DataManager._get(dn.id).edit_in_progress
        assert _DataManager._get(dn.id).editor_id == "foo"
        assert _DataManager._get(dn.id).editor_expiration_date is not None

        dn.unlock_edit("foo")

        assert _DataManager._get(dn.id).last_edit_date is None
        assert len(_DataManager._get(dn.id).properties) == 1
        assert _DataManager._get(dn.id).properties.get("is_generated")
        assert not _DataManager._get(dn.id).edit_in_progress
        assert _DataManager._get(dn.id).editor_id is None
        assert _DataManager._get(dn.id).editor_expiration_date is None

    def test_create_and_get_in_memory_data_node(self):
        # Test we can instantiate an InMemoryDataNode from DataNodeConfig with :
        # - an in_memory type
        # - a scenario scope
        # - an owner id
        # - some default data
        in_memory_dn_config = Config.configure_data_node(
            id="baz", storage_type="in_memory", scope=Scope.SCENARIO, default_data="qux", other_data="foo"
        )
        in_mem_dn = _DataManager._create_and_set(in_memory_dn_config, "Scenario_id", {"task_id"})

        assert isinstance(in_mem_dn, InMemoryDataNode)
        assert isinstance(_DataManager._get(in_mem_dn.id), InMemoryDataNode)

        assert _DataManager._exists(in_mem_dn.id)
        assert _DataManager._get(in_mem_dn.id) is not None
        assert _DataManager._get(in_mem_dn.id).id == in_mem_dn.id
        assert _DataManager._get(in_mem_dn.id).config_id == "baz"
        assert _DataManager._get(in_mem_dn.id).config_id == in_mem_dn.config_id
        assert _DataManager._get(in_mem_dn.id).scope == Scope.SCENARIO
        assert _DataManager._get(in_mem_dn.id).scope == in_mem_dn.scope
        assert _DataManager._get(in_mem_dn.id).owner_id == "Scenario_id"
        assert _DataManager._get(in_mem_dn.id).owner_id == in_mem_dn.owner_id
        assert _DataManager._get(in_mem_dn.id).parent_ids == {"task_id"}
        assert _DataManager._get(in_mem_dn.id).parent_ids == in_mem_dn.parent_ids
        assert _DataManager._get(in_mem_dn.id).last_edit_date is not None
        assert _DataManager._get(in_mem_dn.id).last_edit_date == in_mem_dn.last_edit_date
        assert _DataManager._get(in_mem_dn.id).job_ids == []
        assert _DataManager._get(in_mem_dn.id).job_ids == in_mem_dn.job_ids
        assert _DataManager._get(in_mem_dn.id).is_ready_for_reading
        assert _DataManager._get(in_mem_dn.id).is_ready_for_reading == in_mem_dn.is_ready_for_reading
        assert len(_DataManager._get(in_mem_dn.id).properties) == 1
        assert _DataManager._get(in_mem_dn.id).properties.get("other_data") == "foo"
        assert _DataManager._get(in_mem_dn.id).properties == in_mem_dn.properties

        assert _DataManager._get(in_mem_dn) is not None
        assert _DataManager._get(in_mem_dn).id == in_mem_dn.id
        assert _DataManager._get(in_mem_dn).config_id == "baz"
        assert _DataManager._get(in_mem_dn).config_id == in_mem_dn.config_id
        assert _DataManager._get(in_mem_dn).scope == Scope.SCENARIO
        assert _DataManager._get(in_mem_dn).scope == in_mem_dn.scope
        assert _DataManager._get(in_mem_dn).owner_id == "Scenario_id"
        assert _DataManager._get(in_mem_dn).owner_id == in_mem_dn.owner_id
        assert _DataManager._get(in_mem_dn).parent_ids == {"task_id"}
        assert _DataManager._get(in_mem_dn).parent_ids == in_mem_dn.parent_ids
        assert _DataManager._get(in_mem_dn).last_edit_date is not None
        assert _DataManager._get(in_mem_dn).last_edit_date == in_mem_dn.last_edit_date
        assert _DataManager._get(in_mem_dn).job_ids == []
        assert _DataManager._get(in_mem_dn).job_ids == in_mem_dn.job_ids
        assert _DataManager._get(in_mem_dn).is_ready_for_reading
        assert _DataManager._get(in_mem_dn).is_ready_for_reading == in_mem_dn.is_ready_for_reading
        assert len(_DataManager._get(in_mem_dn).properties) == 1
        assert _DataManager._get(in_mem_dn).properties.get("other_data") == "foo"
        assert _DataManager._get(in_mem_dn).properties == in_mem_dn.properties

    def test_create_and_get_pickle_data_node(self):
        # Test we can instantiate a PickleDataNode from DataNodeConfig with :
        # - an in_memory type
        # - a business cycle scope
        # - No owner id
        # - no default data
        dn_config = Config.configure_data_node(id="plop", storage_type="pickle", scope=Scope.CYCLE)
        pickle_dn = _DataManager._create_and_set(dn_config, None, {"task_id_1", "task_id_2"})

        assert isinstance(pickle_dn, PickleDataNode)
        assert isinstance(_DataManager._get(pickle_dn.id), PickleDataNode)

        assert _DataManager._exists(pickle_dn.id)
        assert _DataManager._get(pickle_dn.id) is not None
        assert _DataManager._get(pickle_dn.id).id == pickle_dn.id
        assert _DataManager._get(pickle_dn.id).config_id == "plop"
        assert _DataManager._get(pickle_dn.id).config_id == pickle_dn.config_id
        assert _DataManager._get(pickle_dn.id).scope == Scope.CYCLE
        assert _DataManager._get(pickle_dn.id).scope == pickle_dn.scope
        assert _DataManager._get(pickle_dn.id).owner_id is None
        assert _DataManager._get(pickle_dn.id).owner_id == pickle_dn.owner_id
        assert _DataManager._get(pickle_dn.id).parent_ids == {"task_id_1", "task_id_2"}
        assert _DataManager._get(pickle_dn.id).parent_ids == pickle_dn.parent_ids
        assert _DataManager._get(pickle_dn.id).last_edit_date is None
        assert _DataManager._get(pickle_dn.id).last_edit_date == pickle_dn.last_edit_date
        assert _DataManager._get(pickle_dn.id).job_ids == []
        assert _DataManager._get(pickle_dn.id).job_ids == pickle_dn.job_ids
        assert not _DataManager._get(pickle_dn.id).is_ready_for_reading
        assert _DataManager._get(pickle_dn.id).is_ready_for_reading == pickle_dn.is_ready_for_reading
        assert len(_DataManager._get(pickle_dn.id).properties) == 1
        assert _DataManager._get(pickle_dn.id).properties == pickle_dn.properties

        assert _DataManager._get(pickle_dn) is not None
        assert _DataManager._get(pickle_dn).id == pickle_dn.id
        assert _DataManager._get(pickle_dn).config_id == "plop"
        assert _DataManager._get(pickle_dn).config_id == pickle_dn.config_id
        assert _DataManager._get(pickle_dn).scope == Scope.CYCLE
        assert _DataManager._get(pickle_dn).scope == pickle_dn.scope
        assert _DataManager._get(pickle_dn).owner_id is None
        assert _DataManager._get(pickle_dn).owner_id == pickle_dn.owner_id
        assert _DataManager._get(pickle_dn).parent_ids == {"task_id_1", "task_id_2"}
        assert _DataManager._get(pickle_dn).parent_ids == pickle_dn.parent_ids
        assert _DataManager._get(pickle_dn).last_edit_date is None
        assert _DataManager._get(pickle_dn).last_edit_date == pickle_dn.last_edit_date
        assert _DataManager._get(pickle_dn).job_ids == []
        assert _DataManager._get(pickle_dn).job_ids == pickle_dn.job_ids
        assert not _DataManager._get(pickle_dn).is_ready_for_reading
        assert _DataManager._get(pickle_dn).is_ready_for_reading == pickle_dn.is_ready_for_reading
        assert len(_DataManager._get(pickle_dn).properties) == 1
        assert _DataManager._get(pickle_dn).properties == pickle_dn.properties

    def test_create_raises_exception_with_wrong_type(self):
        wrong_type_dn_config = DataNodeConfig(id="foo", storage_type="bar", scope=DataNodeConfig._DEFAULT_SCOPE)
        with pytest.raises(InvalidDataNodeType):
            _DataManager._create_and_set(wrong_type_dn_config, None, None)

    def test_create_from_same_config_generates_new_data_node_and_new_id(self):
        dn_config = Config.configure_data_node(id="foo", storage_type="in_memory")
        dn = _DataManager._create_and_set(dn_config, None, None)
        dn_2 = _DataManager._create_and_set(dn_config, None, None)
        assert dn_2.id != dn.id

    def test_create_uses_overridden_attributes_in_config_file(self):
        Config.override(os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/config.toml"))

        csv_dn_cfg = Config.configure_data_node(id="foo", storage_type="csv", path="bar", has_header=True)
        csv_dn = _DataManager._create_and_set(csv_dn_cfg, None, None)
        assert csv_dn.config_id == "foo"
        assert isinstance(csv_dn, CSVDataNode)
        assert csv_dn._path == "path_from_config_file"
        assert csv_dn.has_header

        csv_dn_cfg = Config.configure_data_node(id="baz", storage_type="csv", path="bar", has_header=True)
        csv_dn = _DataManager._create_and_set(csv_dn_cfg, None, None)
        assert csv_dn.config_id == "baz"
        assert isinstance(csv_dn, CSVDataNode)
        assert csv_dn._path == "bar"
        assert csv_dn.has_header

    def test_get_if_not_exists(self):
        with pytest.raises(ModelNotFound):
            _DataManager._repository._load("test_data_node_2")

    def test_get_all(self):
        assert len(_DataManager._get_all()) == 0
        dn_config_1 = Config.configure_data_node(id="foo", storage_type="in_memory")
        _DataManager._create_and_set(dn_config_1, None, None)
        assert len(_DataManager._get_all()) == 1
        dn_config_2 = Config.configure_data_node(id="baz", storage_type="in_memory")
        _DataManager._create_and_set(dn_config_2, None, None)
        _DataManager._create_and_set(dn_config_2, None, None)
        assert len(_DataManager._get_all()) == 3
        assert len([dn for dn in _DataManager._get_all() if dn.config_id == "foo"]) == 1
        assert len([dn for dn in _DataManager._get_all() if dn.config_id == "baz"]) == 2

    def test_get_all_on_multiple_versions_environment(self):
        # Create 5 data nodes with 2 versions each
        # Only version 1.0 has the data node with config_id = "config_id_1"
        # Only version 2.0 has the data node with config_id = "config_id_6"
        for version in range(1, 3):
            for i in range(5):
                _DataManager._set(
                    InMemoryDataNode(
                        f"config_id_{i + version}",
                        Scope.SCENARIO,
                        id=DataNodeId(f"id{i}_v{version}"),
                        version=f"{version}.0",
                    )
                )

        _VersionManager._set_experiment_version("1.0")
        assert len(_DataManager._get_all()) == 5
        assert len(_DataManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
        assert len(_DataManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

        _VersionManager._set_development_version("1.0")
        assert len(_DataManager._get_all()) == 5
        assert len(_DataManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
        assert len(_DataManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

        _VersionManager._set_experiment_version("2.0")
        assert len(_DataManager._get_all()) == 5
        assert len(_DataManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
        assert len(_DataManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1

        _VersionManager._set_development_version("2.0")
        assert len(_DataManager._get_all()) == 5
        assert len(_DataManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
        assert len(_DataManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1

    def test_set(self):
        dn = InMemoryDataNode(
            "config_id",
            Scope.SCENARIO,
            id=DataNodeId("id"),
            owner_id=None,
            parent_ids={"task_id_1"},
            last_edit_date=None,
            edits=[],
            edit_in_progress=False,
            properties={"foo": "bar"},
        )
        assert len(_DataManager._get_all()) == 0
        assert not _DataManager._exists(dn.id)
        _DataManager._set(dn)
        assert len(_DataManager._get_all()) == 1
        assert _DataManager._exists(dn.id)

        # changing data node attribute
        dn._config_id = "foo"
        assert dn.config_id == "foo"
        _DataManager._set(dn)
        assert len(_DataManager._get_all()) == 1
        assert dn.config_id == "foo"
        assert _DataManager._get(dn.id).config_id == "foo"

    def test_delete(self):
        dn_1 = InMemoryDataNode("config_id", Scope.SCENARIO, id="id_1")
        dn_2 = InMemoryDataNode("config_id", Scope.SCENARIO, id="id_2")
        dn_3 = InMemoryDataNode("config_id", Scope.SCENARIO, id="id_3")
        assert len(_DataManager._get_all()) == 0
        _DataManager._set(dn_1)
        _DataManager._set(dn_2)
        _DataManager._set(dn_3)
        assert len(_DataManager._get_all()) == 3
        assert all(_DataManager._exists(dn.id) for dn in [dn_1, dn_2, dn_3])
        _DataManager._delete(dn_1.id)
        assert len(_DataManager._get_all()) == 2
        assert _DataManager._get(dn_2.id).id == dn_2.id
        assert _DataManager._get(dn_3.id).id == dn_3.id
        assert _DataManager._get(dn_1.id) is None
        assert all(_DataManager._exists(dn.id) for dn in [dn_2, dn_3])
        assert not _DataManager._exists(dn_1.id)
        _DataManager._delete_all()
        assert len(_DataManager._get_all()) == 0
        assert not any(_DataManager._exists(dn.id) for dn in [dn_2, dn_3])

    def test_get_or_create(self):
        def _get_or_create_dn(config, *args):
            return _DataManager._bulk_get_or_create([config], *args)[config]

        _DataManager._delete_all()

        global_dn_config = Config.configure_data_node(
            id="test_data_node", storage_type="in_memory", scope=Scope.GLOBAL, data="In memory Data Node"
        )
        cycle_dn_config = Config.configure_data_node(
            id="test_data_node1", storage_type="in_memory", scope=Scope.CYCLE, data="In memory Data Node"
        )
        scenario_dn_config = Config.configure_data_node(
            id="test_data_node2", storage_type="in_memory", scope=Scope.SCENARIO, data="In memory scenario"
        )

        assert len(_DataManager._get_all()) == 0
        global_dn = _get_or_create_dn(global_dn_config, None, None)
        assert len(_DataManager._get_all()) == 1
        global_dn_bis = _get_or_create_dn(global_dn_config, None)
        assert len(_DataManager._get_all()) == 1
        assert global_dn.id == global_dn_bis.id

        scenario_dn = _get_or_create_dn(scenario_dn_config, None, "scenario_id")
        assert len(_DataManager._get_all()) == 2
        scenario_dn_bis = _get_or_create_dn(scenario_dn_config, None, "scenario_id")
        assert len(_DataManager._get_all()) == 2
        assert scenario_dn.id == scenario_dn_bis.id
        scenario_dn_ter = _get_or_create_dn(scenario_dn_config, None, "scenario_id")
        assert len(_DataManager._get_all()) == 2
        assert scenario_dn.id == scenario_dn_bis.id
        assert scenario_dn_bis.id == scenario_dn_ter.id
        scenario_dn_quater = _get_or_create_dn(scenario_dn_config, None, "scenario_id_2")
        assert len(_DataManager._get_all()) == 3
        assert scenario_dn.id == scenario_dn_bis.id
        assert scenario_dn_bis.id == scenario_dn_ter.id
        assert scenario_dn_ter.id != scenario_dn_quater.id

        assert len(_DataManager._get_all()) == 3
        cycle_dn = _get_or_create_dn(cycle_dn_config, "cycle_id", None)
        assert len(_DataManager._get_all()) == 4
        cycle_dn_1 = _get_or_create_dn(cycle_dn_config, "cycle_id", None)
        assert len(_DataManager._get_all()) == 4
        assert cycle_dn.id == cycle_dn_1.id
        cycle_dn_2 = _get_or_create_dn(cycle_dn_config, "cycle_id", "scenario_id")
        assert len(_DataManager._get_all()) == 4
        assert cycle_dn.id == cycle_dn_2.id
        cycle_dn_3 = _get_or_create_dn(cycle_dn_config, "cycle_id", None)
        assert len(_DataManager._get_all()) == 4
        assert cycle_dn.id == cycle_dn_3.id
        cycle_dn_4 = _get_or_create_dn(cycle_dn_config, "cycle_id", "scenario_id")
        assert len(_DataManager._get_all()) == 4
        assert cycle_dn.id == cycle_dn_4.id
        cycle_dn_5 = _get_or_create_dn(cycle_dn_config, "cycle_id", "scenario_id_2")
        assert len(_DataManager._get_all()) == 4
        assert cycle_dn.id == cycle_dn_5.id

        assert cycle_dn_1.id == cycle_dn_2.id
        assert cycle_dn_2.id == cycle_dn_3.id
        assert cycle_dn_3.id == cycle_dn_4.id
        assert cycle_dn_4.id == cycle_dn_5.id

    def test_ensure_persistence_of_data_node(self):
        dm = _DataManager()
        dm._delete_all()

        dn_config_1 = Config.configure_data_node(
            id="data_node_1", storage_type="in_memory", data="In memory sequence 2"
        )
        dn_config_2 = Config.configure_data_node(
            id="data_node_2", storage_type="in_memory", data="In memory sequence 2"
        )

        dm._bulk_get_or_create([dn_config_1, dn_config_2])

        assert len(dm._get_all()) == 2

        # Delete the DataManager to ensure it's get from the storage system
        del dm
        dm = _DataManager()
        dm._bulk_get_or_create([dn_config_1])
        assert len(dm._get_all()) == 2

        dm._delete_all()

    def test_clean_generated_pickle_files(self, pickle_file_path):
        user_pickle_dn_config = Config.configure_data_node(
            id="d1", storage_type="pickle", path=pickle_file_path, default_data="d"
        )
        generated_pickle_dn_1_config = Config.configure_data_node(id="d2", storage_type="pickle", default_data="d")
        generated_pickle_dn_2_config = Config.configure_data_node(id="d3", storage_type="pickle", default_data="d")

        dns = _DataManager._bulk_get_or_create(
            [user_pickle_dn_config, generated_pickle_dn_1_config, generated_pickle_dn_2_config]
        )

        user_pickle_dn = dns[user_pickle_dn_config]
        generated_pickle_dn_1 = dns[generated_pickle_dn_1_config]
        generated_pickle_dn_2 = dns[generated_pickle_dn_2_config]

        _DataManager._clean_pickle_file(user_pickle_dn.id)
        assert file_exists(user_pickle_dn.path)

        _DataManager._clean_pickle_files([generated_pickle_dn_1, generated_pickle_dn_2])
        assert not file_exists(generated_pickle_dn_1.path)
        assert not file_exists(generated_pickle_dn_2.path)

    def test_delete_does_clean_generated_pickle_files(self, pickle_file_path):
        user_pickle_dn_config = Config.configure_data_node(
            id="d1", storage_type="pickle", path=pickle_file_path, default_data="d"
        )
        generated_pickle_dn_config_1 = Config.configure_data_node(id="d2", storage_type="pickle", default_data="d")
        generated_pickle_dn_config_2 = Config.configure_data_node(id="d3", storage_type="pickle", default_data="d")
        generated_pickle_dn_config_3 = Config.configure_data_node(id="d4", storage_type="pickle", default_data="d")

        dns = _DataManager._bulk_get_or_create(
            [
                user_pickle_dn_config,
                generated_pickle_dn_config_1,
                generated_pickle_dn_config_2,
                generated_pickle_dn_config_3,
            ]
        )

        user_pickle_dn = dns[user_pickle_dn_config]
        generated_pickle_dn_1 = dns[generated_pickle_dn_config_1]
        generated_pickle_dn_2 = dns[generated_pickle_dn_config_2]
        generated_pickle_dn_3 = dns[generated_pickle_dn_config_3]

        _DataManager._delete(user_pickle_dn.id)
        assert file_exists(user_pickle_dn.path)

        _DataManager._delete_many([generated_pickle_dn_1.id, generated_pickle_dn_2.id])
        assert not file_exists(generated_pickle_dn_1.path)
        assert not file_exists(generated_pickle_dn_2.path)

        _DataManager._delete_all()
        assert not file_exists(generated_pickle_dn_3.path)

    def test_create_dn_from_loaded_config_no_scope(self):
        file_config = NamedTemporaryFile(
            """
            [TAIPY]

            [DATA_NODE.a]
            default_data = "4:int"

            [DATA_NODE.b]

            [TASK.t]
            function = "math.sqrt:function"
            inputs = [ "a:SECTION",]
            outputs = [ "b:SECTION",]
            skippable = "False:bool"

            [SCENARIO.s]
            tasks = [ "t:SECTION",]
            sequences.s_sequence = [ "t:SECTION",]

            [SCENARIO.s.comparators]
            """
        )
        from taipy import core as tp

        Config.override(file_config.filename)
        tp.create_scenario(Config.scenarios["s"])
        tp.create_scenario(Config.scenarios["s"])

        assert len(tp.get_data_nodes()) == 4

    def test_create_dn_from_loaded_config_no_storage_type(self):
        file_config = NamedTemporaryFile(
            """
            [TAIPY]

            [DATA_NODE.input_dn]
            scope = "SCENARIO:SCOPE"
            default_data = "21:int"

            [DATA_NODE.output_dn]
            storage_type = "in_memory"
            scope = "SCENARIO:SCOPE"

            [TASK.double]
            inputs = [ "input_dn:SECTION",]
            function = "math.sqrt:function"
            outputs = [ "output_dn:SECTION",]
            skippable = "False:bool"

            [SCENARIO.my_scenario]
            tasks = [ "double:SECTION",]
            sequences.my_sequence = [ "double:SECTION",]

            [SCENARIO.my_scenario.comparators]
            """
        )
        from taipy import core as tp

        Config.override(file_config.filename)
        scenario = tp.create_scenario(Config.scenarios["my_scenario"])

        assert isinstance(scenario.input_dn, PickleDataNode)
        assert isinstance(scenario.output_dn, InMemoryDataNode)

    def test_create_dn_from_loaded_config_modified_default_config(self):
        file_config = NamedTemporaryFile(
            """
            [TAIPY]

            [DATA_NODE.input_dn]
            scope = "SCENARIO:SCOPE"
            default_path="fake/path.csv"

            [DATA_NODE.output_dn]
            storage_type = "in_memory"
            scope = "SCENARIO:SCOPE"

            [TASK.double]
            inputs = [ "input_dn:SECTION",]
            function = "math.sqrt:function"
            outputs = [ "output_dn:SECTION",]
            skippable = "False:bool"

            [SCENARIO.my_scenario]
            tasks = [ "double:SECTION",]
            sequences.my_sequence = [ "double:SECTION",]

            [SCENARIO.my_scenario.comparators]
            """
        )
        from taipy import core as tp

        Config.set_default_data_node_configuration(storage_type="csv")
        Config.override(file_config.filename)
        scenario = tp.create_scenario(Config.scenarios["my_scenario"])

        assert isinstance(scenario.input_dn, CSVDataNode)
        assert isinstance(scenario.output_dn, InMemoryDataNode)

    def test_get_tasks_by_config_id(self):
        dn_config_1 = Config.configure_data_node("dn_1", scope=Scope.SCENARIO)
        dn_config_2 = Config.configure_data_node("dn_2", scope=Scope.SCENARIO)
        dn_config_3 = Config.configure_data_node("dn_3", scope=Scope.SCENARIO)

        dn_1_1 = _DataManager._create_and_set(dn_config_1, None, None)
        dn_1_2 = _DataManager._create_and_set(dn_config_1, None, None)
        dn_1_3 = _DataManager._create_and_set(dn_config_1, None, None)
        assert len(_DataManager._get_all()) == 3

        dn_2_1 = _DataManager._create_and_set(dn_config_2, None, None)
        dn_2_2 = _DataManager._create_and_set(dn_config_2, None, None)
        assert len(_DataManager._get_all()) == 5

        dn_3_1 = _DataManager._create_and_set(dn_config_3, None, None)
        assert len(_DataManager._get_all()) == 6

        dn_1_datanodes = _DataManager._get_by_config_id(dn_config_1.id)
        assert len(dn_1_datanodes) == 3
        assert sorted([dn_1_1.id, dn_1_2.id, dn_1_3.id]) == sorted([sequence.id for sequence in dn_1_datanodes])

        dn_2_datanodes = _DataManager._get_by_config_id(dn_config_2.id)
        assert len(dn_2_datanodes) == 2
        assert sorted([dn_2_1.id, dn_2_2.id]) == sorted([sequence.id for sequence in dn_2_datanodes])

        dn_3_datanodes = _DataManager._get_by_config_id(dn_config_3.id)
        assert len(dn_3_datanodes) == 1
        assert sorted([dn_3_1.id]) == sorted([sequence.id for sequence in dn_3_datanodes])

    def test_get_data_nodes_by_config_id_in_multiple_versions_environment(self):
        dn_config_1 = Config.configure_data_node("dn_1", scope=Scope.SCENARIO)
        dn_config_2 = Config.configure_data_node("dn_2", scope=Scope.SCENARIO)

        _VersionManager._set_experiment_version("1.0")
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_2, None, None)
        _DataManager._create_and_set(dn_config_2, None, None)

        assert len(_DataManager._get_by_config_id(dn_config_1.id)) == 3
        assert len(_DataManager._get_by_config_id(dn_config_2.id)) == 2

        _VersionManager._set_experiment_version("2.0")
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_1, None, None)
        _DataManager._create_and_set(dn_config_2, None, None)
        _DataManager._create_and_set(dn_config_2, None, None)

        assert len(_DataManager._get_by_config_id(dn_config_1.id)) == 3
        assert len(_DataManager._get_by_config_id(dn_config_2.id)) == 2
