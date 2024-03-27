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
from importlib import util

import numpy as np
import pandas as pd
import pytest

from taipy.config.common.scope import Scope
from taipy.core.data.parquet import ParquetDataNode
from taipy.core.exceptions.exceptions import NoData


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


class MyCustomXYObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def create_custom_class(**kwargs):
    return MyOtherCustomObject(id=kwargs["id"], sentence=kwargs["text"])


def create_custom_xy_class(**kwargs):
    return MyCustomXYObject(x=kwargs["x"], y=kwargs["y"])


class TestReadParquetDataNode:
    __engine = ["pyarrow"]
    if util.find_spec("fastparquet"):
        __engine.append("fastparquet")

    @pytest.mark.parametrize("engine", __engine)
    def test_raise_no_data(self, engine, parquet_file_path):
        not_existing_parquet = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": "nonexistent.parquet", "engine": engine}
        )
        with pytest.raises(NoData):
            assert not_existing_parquet.read() is None
            not_existing_parquet.read_or_raise()

    @pytest.mark.parametrize("engine", __engine)
    def test_read_parquet_file_pandas(self, engine, parquet_file_path):
        df = pd.read_parquet(parquet_file_path)
        parquet_data_node_as_pandas = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_file_path, "engine": engine}
        )
        data_pandas = parquet_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 2
        assert data_pandas.equals(df)

    @pytest.mark.parametrize("engine", __engine)
    def test_read_parquet_file_numpy(self, engine, parquet_file_path):
        df = pd.read_parquet(parquet_file_path)
        parquet_data_node_as_numpy = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_file_path, "exposed_type": "numpy", "engine": engine}
        )
        data_numpy = parquet_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 2
        assert np.array_equal(data_numpy, df.to_numpy())

    def test_read_custom_exposed_type(self):
        example_parquet_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.parquet")

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": MyCustomObject}
        )
        assert all(isinstance(obj, MyCustomObject) for obj in dn.read())

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": create_custom_class}
        )
        assert all(isinstance(obj, MyOtherCustomObject) for obj in dn.read())

    @pytest.mark.parametrize("engine", __engine)
    def test_read_parquet_folder_pandas(self, engine):
        parquet_folder_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/parquet_example")

        df = pd.read_parquet(parquet_folder_path)
        parquet_data_node_as_pandas = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_folder_path, "engine": engine}
        )
        data_pandas = parquet_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 5
        assert data_pandas.equals(df)

    @pytest.mark.parametrize("engine", __engine)
    def test_read_parquet_folder_numpy(self, engine):
        parquet_folder_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/parquet_example")

        df = pd.read_parquet(parquet_folder_path)
        parquet_data_node_as_pandas = ParquetDataNode(
            "bar", Scope.SCENARIO, properties={"path": parquet_folder_path, "engine": engine, "exposed_type": "numpy"}
        )
        data_numpy = parquet_data_node_as_pandas.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 5
        assert np.array_equal(data_numpy, df.to_numpy())

    def test_read_folder_custom_exposed_type(self):
        example_parquet_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/parquet_example")

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": MyCustomXYObject}
        )
        dn.read()
        assert all(isinstance(obj, MyCustomXYObject) for obj in dn.read())

        dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": example_parquet_path, "exposed_type": create_custom_xy_class}
        )
        assert all(isinstance(obj, MyCustomXYObject) for obj in dn.read())

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

    @pytest.mark.parametrize("engine", __engine)
    def test_read_pandas_parquet_config_kwargs(self, engine, tmpdir_factory):
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

    def test_read_with_kwargs_never_written(self):
        path = "data/node/path"
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": path})
        assert dn.read_with_kwargs() is None
