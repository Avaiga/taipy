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

import os
import pathlib

import pytest
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core._version._version_manager import _VersionManager
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.exceptions.exceptions import InvalidDataNodeType, ModelNotFound


def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)


def init_managers():
    _DataManagerFactory._build_manager()._delete_all()


class TestDataManager:
    def test_create_data_node_and_modify_properties_does_not_modify_config(self, init_sql_repo):
        init_managers()

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

    def test_create_raises_exception_with_wrong_type(self, init_sql_repo):
        init_managers()

        wrong_type_dn_config = DataNodeConfig(id="foo", storage_type="bar", scope=DataNodeConfig._DEFAULT_SCOPE)
        with pytest.raises(InvalidDataNodeType):
            _DataManager._create_and_set(wrong_type_dn_config, None, None)

    def test_create_from_same_config_generates_new_data_node_and_new_id(self, init_sql_repo):
        init_managers()

        dn_config = Config.configure_data_node(id="foo", storage_type="in_memory")
        dn = _DataManager._create_and_set(dn_config, None, None)
        dn_2 = _DataManager._create_and_set(dn_config, None, None)
        assert dn_2.id != dn.id

    def test_create_uses_overridden_attributes_in_config_file(self, init_sql_repo):
        init_managers()

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

    def test_get_if_not_exists(self, init_sql_repo):
        init_managers()

        with pytest.raises(ModelNotFound):
            _DataManager._repository._load("test_data_node_2")

    def test_get_all(self, init_sql_repo):
        init_managers()

        _DataManager._delete_all()
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

    def test_get_all_on_multiple_versions_environment(self, init_sql_repo):
        init_managers()

        # Create 5 data nodes with 2 versions each
        # Only version 1.0 has the data node with config_id = "config_id_1"
        # Only version 2.0 has the data node with config_id = "config_id_6"
        for version in range(1, 3):
            for i in range(5):
                _DataManager._set(
                    InMemoryDataNode(
                        f"config_id_{i+version}",
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

    def test_set(self, init_sql_repo):
        init_managers()

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
        dn.config_id = "foo"
        assert dn.config_id == "foo"
        _DataManager._set(dn)
        assert len(_DataManager._get_all()) == 1
        assert dn.config_id == "foo"
        assert _DataManager._get(dn.id).config_id == "foo"

    def test_delete(self, init_sql_repo):
        init_managers()
        _DataManager._delete_all()

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

    def test_get_or_create(self, init_sql_repo):
        def _get_or_create_dn(config, *args):
            return _DataManager._bulk_get_or_create([config], *args)[config]

        init_managers()

        global_dn_config = Config.configure_data_node(
            id="test_data_node", storage_type="in_memory", scope=Scope.GLOBAL, data="In memory Data Node"
        )
        cycle_dn_config = Config.configure_data_node(
            id="test_data_node1", storage_type="in_memory", scope=Scope.CYCLE, data="In memory scenario"
        )
        scenario_dn_config = Config.configure_data_node(
            id="test_data_node2", storage_type="in_memory", scope=Scope.SCENARIO, data="In memory scenario"
        )

        _DataManager._delete_all()

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

    def test_get_data_nodes_by_config_id(self, init_sql_repo):
        init_managers()

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

    def test_get_data_nodes_by_config_id_in_multiple_versions_environment(self, init_sql_repo):
        init_managers()

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
