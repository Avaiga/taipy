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
from importlib import util
from time import sleep

import pandas as pd
import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.parquet import ParquetDataNode
from taipy.core.exceptions.exceptions import (
    InvalidExposedType,
    UnknownCompressionAlgorithm,
    UnknownParquetEngine,
)


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.parquet")
    if os.path.isfile(path):
        os.remove(path)


class MyCustomObject:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


class MyOtherCustomObject:
    def __init__(self, id, sentence):
        self.id = id
        self.sentence = sentence


def create_custom_class(**kwargs):
    return MyOtherCustomObject(id=kwargs["id"], sentence=kwargs["text"])


class TestParquetDataNode:
    __engine = ["pyarrow"]
    if util.find_spec("fastparquet"):
        __engine.append("fastparquet")

    def test_create(self):
        path = "data/node/path"
        compression = "snappy"
        dn = ParquetDataNode(
            "foo_bar", Scope.SCENARIO, properties={"path": path, "compression": compression, "name": "super name"}
        )
        assert isinstance(dn, ParquetDataNode)
        assert dn.storage_type() == "parquet"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.exposed_type == "pandas"
        assert dn.compression == "snappy"
        assert dn.engine == "pyarrow"

        with pytest.raises(InvalidConfigurationId):
            dn = ParquetDataNode("foo bar", Scope.SCENARIO, properties={"path": path, "name": "super name"})

    def test_get_user_properties(self, parquet_file_path):
        dn_1 = ParquetDataNode("dn_1", Scope.SCENARIO, properties={"path": parquet_file_path})
        assert dn_1._get_user_properties() == {}

        dn_2 = ParquetDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "exposed_type": "numpy",
                "default_data": "foo",
                "default_path": parquet_file_path,
                "engine": "pyarrow",
                "compression": "snappy",
                "read_kwargs": {"columns": ["a", "b"]},
                "write_kwargs": {"index": False},
                "foo": "bar",
            },
        )

        # exposed_type, default_data, default_path, path, engine, compression, read_kwargs, write_kwargs
        # are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_new_parquet_data_node_with_existing_file_is_ready_for_reading(self, parquet_file_path):
        not_ready_dn_cfg = Config.configure_data_node(
            "not_ready_data_node_config_id", "parquet", path="NOT_EXISTING.parquet"
        )
        not_ready_dn = _DataManager._bulk_get_or_create([not_ready_dn_cfg])[not_ready_dn_cfg]
        assert not not_ready_dn.is_ready_for_reading

        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "parquet", path=parquet_file_path)
        ready_dn = _DataManager._bulk_get_or_create([ready_dn_cfg])[ready_dn_cfg]
        assert ready_dn.is_ready_for_reading

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({}, False),
            ({"default_data": {"a": ["foo", "bar"]}}, True),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = ParquetDataNode("foo", Scope.SCENARIO, DataNodeId(f"dn_id_{uuid.uuid4()}"), properties=properties)
        assert dn.path == os.path.join(Config.core.storage_folder.strip("/"), "parquets", dn.id + ".parquet")
        assert os.path.exists(dn.path) is exists

    @pytest.mark.parametrize("engine", __engine)
    def test_modin_deprecated_in_favor_of_pandas(self, engine, parquet_file_path):
        # Create ParquetDataNode with modin exposed_type
        props = {"path": parquet_file_path, "exposed_type": "modin", "engine": engine}
        parquet_data_node_as_modin = ParquetDataNode("bar", Scope.SCENARIO, properties=props)
        assert parquet_data_node_as_modin.properties["exposed_type"] == "pandas"
        data_modin = parquet_data_node_as_modin.read()
        assert isinstance(data_modin, pd.DataFrame)

    def test_set_path(self):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": "foo.parquet"})
        assert dn.path == "foo.parquet"
        dn.path = "bar.parquet"
        assert dn.path == "bar.parquet"

    def test_raise_error_unknown_parquet_engine(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")
        with pytest.raises(UnknownParquetEngine):
            ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path, "engine": "foo"})

    def test_raise_error_unknown_compression_algorithm(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")
        with pytest.raises(UnknownCompressionAlgorithm):
            ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path, "compression": "foo"})

    def test_raise_error_invalid_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")
        with pytest.raises(InvalidExposedType):
            ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "foo"})

    def test_get_system_file_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        pd.DataFrame([]).to_parquet(temp_file_path)
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})

        dn.write(pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]}))
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame(pd.DataFrame(data={"col1": [5, 6], "col2": [7, 8]})).to_parquet(temp_file_path)
        new_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write(pd.DataFrame(data={"col1": [9, 10], "col2": [10, 12]}))
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)

    def test_get_system_folder_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_folder_path = tmpdir_factory.mktemp("data").strpath
        temp_file_path = os.path.join(temp_folder_path, "temp.parquet")
        pd.DataFrame([]).to_parquet(temp_file_path)

        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_folder_path})
        initial_edit_date = dn.last_edit_date

        # Sleep so that the file can be created successfully on Ubuntu
        sleep(0.1)

        pd.DataFrame(pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})).to_parquet(temp_file_path)
        first_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))
        assert dn.last_edit_date > initial_edit_date
        assert dn.last_edit_date == first_edit_date

        sleep(0.1)

        pd.DataFrame(pd.DataFrame(data={"col1": [5, 6], "col2": [7, 8]})).to_parquet(temp_file_path)
        second_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))
        assert dn.last_edit_date > first_edit_date
        assert dn.last_edit_date == second_edit_date

        os.unlink(temp_file_path)

    def test_migrate_to_new_path(self, tmp_path):
        _base_path = os.path.join(tmp_path, ".data")
        path = os.path.join(_base_path, "test.parquet")
        # create a file on old path
        os.mkdir(_base_path)
        with open(path, "w"):
            pass

        dn = ParquetDataNode("foo_bar", Scope.SCENARIO, properties={"path": path, "name": "super name"})

        assert ".data" not in dn.path
        assert os.path.exists(dn.path)
