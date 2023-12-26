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
from datetime import datetime
from importlib import util
from time import sleep

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
import pytest
from modin.pandas.test.utils import df_equals
from pandas.testing import assert_frame_equal
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.parquet import ParquetDataNode
from taipy.core.exceptions.exceptions import (
    InvalidExposedType,
    NoData,
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
        dn = ParquetDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)
        assert os.path.exists(dn.path) is exists

    @pytest.mark.parametrize("engine", __engine)
    def test_read_file(self, engine, parquet_file_path):
        not_existing_parquet = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": "nonexistent.parquet", "engine": engine}
        )
        with pytest.raises(NoData):
            assert not_existing_parquet.read() is None
            not_existing_parquet.read_or_raise()

        df = pd.read_parquet(parquet_file_path)
        # Create ParquetDataNode without exposed_type (Default is pandas.DataFrame)
        parquet_data_node_as_pandas = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_file_path, "engine": engine}
        )
        data_pandas = parquet_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 2
        assert data_pandas.equals(df)
        assert np.array_equal(data_pandas.to_numpy(), df.to_numpy())

        # Create ParquetDataNode with numpy exposed_type
        parquet_data_node_as_numpy = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "numpy", "engine": engine}
        )
        data_numpy = parquet_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 2
        assert np.array_equal(data_numpy, df.to_numpy())

    @pytest.mark.modin
    @pytest.mark.parametrize("engine", __engine)
    def test_read_file_modin(self, engine, parquet_file_path):
        df = pd.read_parquet(parquet_file_path)
        # Create ParquetDataNode with modin exposed_type
        parquet_data_node_as_modin = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "modin", "engine": engine}
        )
        data_modin = parquet_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 2
        assert data_modin.equals(df)
        assert np.array_equal(data_modin.to_numpy(), df.to_numpy())

    @pytest.mark.parametrize("engine", __engine)
    def test_read_folder(self, engine):
        parquet_folder_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/parquet_example")

        df = pd.read_parquet(parquet_folder_path)
        parquet_data_node_as_pandas = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_folder_path, "engine": engine}
        )
        data_pandas = parquet_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 5
        assert data_pandas.equals(df)
        assert np.array_equal(data_pandas.to_numpy(), df.to_numpy())

    def test_set_path(self):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": "foo.parquet"})
        assert dn.path == "foo.parquet"
        dn.path = "bar.parquet"
        assert dn.path == "bar.parquet"

    @pytest.mark.parametrize("engine", __engine)
    def test_read_write_after_modify_path(self, engine):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.parquet")
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path, "engine": engine})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write(read_data)
        assert dn.read().equals(read_data)

    def test_read_custom_exposed_type(self):
        example_parquet_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": MyCustomObject}
        )
        assert all([isinstance(obj, MyCustomObject) for obj in dn.read()])

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": create_custom_class}
        )
        assert all([isinstance(obj, MyOtherCustomObject) for obj in dn.read()])

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

    def test_read_empty_data(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        empty_df = pd.DataFrame([])
        empty_df.to_parquet(temp_file_path)

        # Pandas
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})
        assert dn.read().equals(empty_df)

        # Numpy
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "numpy"})
        assert np.array_equal(dn.read(), empty_df.to_numpy())

        # Custom
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": MyCustomObject})
        assert dn.read() == []

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

    @pytest.mark.skipif(not util.find_spec("fastparquet"), reason="Append parquet requires fastparquet to be installed")
    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
        ],
    )
    def test_append_pandas(self, parquet_file_path, default_data_frame, content):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": parquet_file_path})
        assert_frame_equal(dn.read(), default_data_frame)

        dn.append(content)
        assert_frame_equal(
            dn.read(),
            pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(drop=True),
        )

    @pytest.mark.modin
    @pytest.mark.skipif(not util.find_spec("fastparquet"), reason="Append parquet requires fastparquet to be installed")
    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
        ],
    )
    def test_append_modin(self, parquet_file_path, default_data_frame, content):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "modin"})
        df_equals(dn.read(), modin_pd.DataFrame(default_data_frame))

        dn.append(content)
        df_equals(
            dn.read(),
            modin_pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(
                drop=True
            ),
        )

    @pytest.mark.parametrize(
        "data",
        [
            [{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}],
            pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
        ],
    )
    def test_write_to_disk(self, tmpdir_factory, data):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path})
        dn.write(data)

        assert pathlib.Path(temp_file_path).exists()
        assert isinstance(dn.read(), pd.DataFrame)

        @pytest.mark.modin
        @pytest.mark.parametrize(
            "data",
            [
                modin_pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            ],
        )
        def test_write_to_disk_modin(self, tmpdir_factory, data):
            temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
            dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path})
            dn.write(data)

            assert pathlib.Path(temp_file_path).exists()
            assert isinstance(dn.read(), pd.DataFrame)

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "data",
        [
            modin_pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
        ],
    )
    def test_write_to_disk_modin(self, tmpdir_factory, data):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path})
        dn.write(data)

        assert pathlib.Path(temp_file_path).exists()
        assert isinstance(dn.read(), pd.DataFrame)

    def test_filter_pandas_exposed_type(self, parquet_file_path):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "pandas"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        # Test datanode indexing and slicing
        assert dn["foo"].equals(pd.Series([1, 1, 1, 2, None]))
        assert dn["bar"].equals(pd.Series([1, 2, None, 2, 2]))
        assert dn[:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}, {"foo": 1.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = pd.DataFrame([{"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("bar", 2, Operator.EQUAL))
        filtered_by_indexing = dn[dn["bar"] == 2]
        expected_data = pd.DataFrame([{"foo": 1.0, "bar": 2.0}, {"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = pd.DataFrame(
            [
                {"foo": 1.0, "bar": 1.0},
                {"foo": 1.0, "bar": 2.0},
                {"foo": 2.0, "bar": 2.0},
                {"bar": 2.0},
            ]
        )
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    @pytest.mark.modin
    def test_filter_modin_exposed_type(self, parquet_file_path):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "modin"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        # Test datanode indexing and slicing
        assert dn["foo"].equals(modin_pd.Series([1, 1, 1, 2, None]))
        assert dn["bar"].equals(modin_pd.Series([1, 2, None, 2, 2]))
        assert dn[:2].equals(modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}, {"foo": 1.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = modin_pd.DataFrame([{"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("bar", 2, Operator.EQUAL))
        filtered_by_indexing = dn[dn["bar"] == 2]
        expected_data = modin_pd.DataFrame([{"foo": 1.0, "bar": 2.0}, {"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = modin_pd.DataFrame(
            [
                {"foo": 1.0, "bar": 1.0},
                {"foo": 1.0, "bar": 2.0},
                {"foo": 2.0, "bar": 2.0},
                {"bar": 2.0},
            ]
        )
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

    def test_filter_numpy_exposed_type(self, parquet_file_path):
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "numpy"})
        dn.write(
            [
                [1, 1],
                [1, 2],
                [1, 3],
                [2, 1],
                [2, 2],
                [2, 3],
            ]
        )

        # Test datanode indexing and slicing
        assert np.array_equal(dn[0], np.array([1, 1]))
        assert np.array_equal(dn[1], np.array([1, 2]))
        assert np.array_equal(dn[:3], np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn[:, 0], np.array([1, 1, 1, 2, 2, 2]))
        assert np.array_equal(dn[1:4, :1], np.array([[1], [1], [2]]))

        # Test filter data
        assert np.array_equal(dn.filter((0, 1, Operator.EQUAL)), np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn[dn[:, 0] == 1], np.array([[1, 1], [1, 2], [1, 3]]))

        assert np.array_equal(dn.filter((0, 1, Operator.NOT_EQUAL)), np.array([[2, 1], [2, 2], [2, 3]]))
        assert np.array_equal(dn[dn[:, 0] != 1], np.array([[2, 1], [2, 2], [2, 3]]))

        assert np.array_equal(dn.filter((1, 2, Operator.EQUAL)), np.array([[1, 2], [2, 2]]))
        assert np.array_equal(dn[dn[:, 1] == 2], np.array([[1, 2], [2, 2]]))

        assert np.array_equal(
            dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR),
            np.array([[1, 1], [1, 2], [2, 1], [2, 2]]),
        )
        assert np.array_equal(dn[(dn[:, 1] == 1) | (dn[:, 1] == 2)], np.array([[1, 1], [1, 2], [2, 1], [2, 2]]))

    @pytest.mark.parametrize("engine", __engine)
    def test_pandas_parquet_config_kwargs(self, engine, tmpdir_factory):
        read_kwargs = {"filters": [("integer", "<", 10)], "columns": ["integer"]}
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": temp_file_path, "engine": engine, "read_kwargs": read_kwargs}
        )

        df = pd.read_csv(os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv"))
        dn.write(df)

        assert set(pd.read_parquet(temp_file_path).columns) == {"id", "integer", "text"}
        assert set(dn.read().columns) == set(read_kwargs["columns"])

        # !!! filter doesn't work with `fastparquet` without partition_cols
        if engine == "pyarrow":
            assert len(dn.read()) != len(df)
            assert len(dn.read()) == 2

    @pytest.mark.parametrize("engine", __engine)
    def test_kwarg_precedence(self, engine, tmpdir_factory, default_data_frame):
        # Precedence:
        # 1. Class read/write methods
        # 2. Defined in read_kwargs and write_kwargs, in properties
        # 3. Defined top-level in properties

        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        temp_file_2_path = str(tmpdir_factory.mktemp("data").join("temp_2.parquet"))
        df = default_data_frame.copy(deep=True)

        # Write
        # 3
        comp3 = "snappy"
        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": temp_file_path, "engine": engine, "compression": comp3}
        )
        dn.write(df)
        df.to_parquet(path=temp_file_2_path, compression=comp3, engine=engine)
        with open(temp_file_2_path, "rb") as tf:
            with pathlib.Path(temp_file_path).open("rb") as f:
                assert f.read() == tf.read()

        # 3 and 2
        comp2 = "gzip"
        dn = ParquetDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "path": temp_file_path,
                "engine": engine,
                "compression": comp3,
                "write_kwargs": {"compression": comp2},
            },
        )
        dn.write(df)
        df.to_parquet(path=temp_file_2_path, compression=comp2, engine=engine)
        with open(temp_file_2_path, "rb") as tf:
            with pathlib.Path(temp_file_path).open("rb") as f:
                assert f.read() == tf.read()

        # 3, 2 and 1
        comp1 = "brotli"
        dn = ParquetDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "path": temp_file_path,
                "engine": engine,
                "compression": comp3,
                "write_kwargs": {"compression": comp2},
            },
        )
        dn.write_with_kwargs(df, compression=comp1)
        df.to_parquet(path=temp_file_2_path, compression=comp1, engine=engine)
        with open(temp_file_2_path, "rb") as tf:
            with pathlib.Path(temp_file_path).open("rb") as f:
                assert f.read() == tf.read()

        # Read
        df.to_parquet(temp_file_path, engine=engine)
        # 2
        cols2 = ["a", "b"]
        dn = ParquetDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": temp_file_path, "engine": engine, "read_kwargs": {"columns": cols2}},
        )
        assert set(dn.read().columns) == set(cols2)

        # 1
        cols1 = ["a"]
        dn = ParquetDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": temp_file_path, "engine": engine, "read_kwargs": {"columns": cols2}},
        )
        assert set(dn.read_with_kwargs(columns=cols1).columns) == set(cols1)

    def test_partition_cols(self, tmpdir_factory, default_data_frame: pd.DataFrame):
        temp_dir_path = str(tmpdir_factory.mktemp("data").join("temp_dir"))

        write_kwargs = {"partition_cols": ["a", "b"]}
        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": temp_dir_path, "write_kwargs": write_kwargs}
        )  # type: ignore
        dn.write(default_data_frame)

        assert pathlib.Path(temp_dir_path).is_dir()
        # dtypes change during round-trip with partition_cols
        pd.testing.assert_frame_equal(
            dn.read().sort_index(axis=1),
            default_data_frame.sort_index(axis=1),
            check_dtype=False,
            check_categorical=False,
        )

    def test_read_with_kwargs_never_written(self):
        path = "data/node/path"
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path})
        assert dn.read_with_kwargs() is None
