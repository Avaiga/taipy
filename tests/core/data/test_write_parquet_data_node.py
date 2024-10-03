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
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.core.data.parquet import ParquetDataNode


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

    def __eq__(self, value) -> bool:
        return self.id == value.id and self.integer == value.integer and self.text == value.text


class MyOtherCustomObject:
    def __init__(self, id, sentence):
        self.id = id
        self.sentence = sentence


def create_custom_class(**kwargs):
    return MyOtherCustomObject(id=kwargs["id"], sentence=kwargs["text"])


class TestWriteParquetDataNode:
    __engine = ["pyarrow"]
    if util.find_spec("fastparquet"):
        __engine.append("fastparquet")

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

    def test_write_pandas(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        parquet_dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path})

        df = pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])
        parquet_dn.write(df)

        assert pathlib.Path(temp_file_path).exists()

        dn_data = parquet_dn.read()

        assert isinstance(dn_data, pd.DataFrame)
        assert dn_data.equals(df)

        parquet_dn.write(df["a"])
        assert pd.DataFrame.equals(parquet_dn.read(), df[["a"]])

        series = pd.Series([1, 2, 3])
        parquet_dn.write(series)
        assert np.array_equal(parquet_dn.read().to_numpy(), pd.DataFrame(series).to_numpy())

        parquet_dn.write(None)
        assert parquet_dn.read().empty

    def test_write_numpy(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        parquet_dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "numpy"}
        )

        arr = np.array([[1], [2], [3], [4], [5]])
        parquet_dn.write(arr)
        assert np.array_equal(parquet_dn.read(), arr)

        arr = arr[0:3]
        parquet_dn.write(arr)
        assert np.array_equal(parquet_dn.read(), arr)

        parquet_dn.write(None)
        assert parquet_dn.read().size == 0

    def test_write_custom_exposed_type(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.parquet"))
        parquet_dn = ParquetDataNode(
            "foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": MyCustomObject}
        )

        data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
        parquet_dn.write(data)
        assert all(actual == expected for actual, expected in zip(parquet_dn.read(), data))

        parquet_dn.write(None)
        assert parquet_dn.read() == []

    @pytest.mark.parametrize("engine", __engine)
    def test_write_kwarg_precedence(self, engine, tmpdir_factory, default_data_frame):
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
        dn._write_with_kwargs(df, compression=comp1)
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
        dn = ParquetDataNode("foo", Scope.SCENARIO, properties={"path": temp_dir_path, "write_kwargs": write_kwargs})  # type: ignore
        dn.write(default_data_frame)

        assert pathlib.Path(temp_dir_path).is_dir()
        # dtypes change during round-trip with partition_cols
        pd.testing.assert_frame_equal(
            dn.read().sort_index(axis=1),
            default_data_frame.sort_index(axis=1),
            check_dtype=False,
            check_categorical=False,
        )

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
