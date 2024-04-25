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
import uuid
from datetime import datetime
from time import sleep

import pandas as pd
import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.exceptions.exceptions import InvalidExposedType


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
    if os.path.isfile(path):
        os.remove(path)


class TestCSVDataNode:
    def test_create(self):
        path = "data/node/path"
        dn = CSVDataNode(
            "foo_bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "name": "super name"}
        )
        assert isinstance(dn, CSVDataNode)
        assert dn.storage_type() == "csv"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False
        assert dn.exposed_type == "pandas"

        with pytest.raises(InvalidConfigurationId):
            CSVDataNode("foo bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "name": "super name"})

    def test_modin_deprecated_in_favor_of_pandas(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode with modin exposed_type
        csv_data_node_as_modin = CSVDataNode("bar", Scope.SCENARIO, properties={"path": path, "exposed_type": "modin"})
        assert csv_data_node_as_modin.properties["exposed_type"] == "pandas"
        data_modin = csv_data_node_as_modin.read()
        assert isinstance(data_modin, pd.DataFrame)

    def test_get_user_properties(self, csv_file):
        dn_1 = CSVDataNode("dn_1", Scope.SCENARIO, properties={"path": "data/node/path"})
        assert dn_1._get_user_properties() == {}

        dn_2 = CSVDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "exposed_type": "numpy",
                "default_data": "foo",
                "default_path": csv_file,
                "has_header": False,
                "foo": "bar",
            },
        )

        # exposed_type, default_data, default_path, path, has_header, sheet_name are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_new_csv_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "csv", path="NOT_EXISTING.csv")
        not_ready_dn = _DataManager._bulk_get_or_create([not_ready_dn_cfg])[not_ready_dn_cfg]
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "csv", path=path)
        ready_dn = _DataManager._bulk_get_or_create([ready_dn_cfg])[ready_dn_cfg]
        assert ready_dn.is_ready_for_reading

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({}, False),
            ({"default_data": ["foo", "bar"]}, True),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = CSVDataNode("foo", Scope.SCENARIO, DataNodeId(f"dn_id_{uuid.uuid4()}"), properties=properties)
        assert dn.path == os.path.join(Config.core.storage_folder.strip("/"), "csvs", dn.id + ".csv")
        assert os.path.exists(dn.path) is exists

    def test_set_path(self):
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.csv"})
        assert dn.path == "foo.csv"
        dn.path = "bar.csv"
        assert dn.path == "bar.csv"

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write(read_data)
        assert dn.read().equals(read_data)

    def test_pandas_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        assert isinstance(dn.read(), pd.DataFrame)

    def test_raise_error_invalid_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        with pytest.raises(InvalidExposedType):
            CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "foo"})

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.csv"))
        pd.DataFrame([]).to_csv(temp_file_path)
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})

        dn.write(pd.DataFrame([1, 2, 3]))
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame([4, 5, 6]).to_csv(temp_file_path)
        new_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write(pd.DataFrame([7, 8, 9]))
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)

    def test_migrate_to_new_path(self, tmp_path):
        _base_path = os.path.join(tmp_path, ".data")
        path = os.path.join(_base_path, "test.csv")
        # create a file on old path
        os.mkdir(_base_path)
        with open(path, "w"):
            pass

        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})

        assert ".data" not in dn.path
        assert os.path.exists(dn.path)
