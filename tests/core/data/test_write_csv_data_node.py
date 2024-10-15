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

import dataclasses
import os
import pathlib

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.common.config.common.scope import Scope
from taipy.core.data.csv import CSVDataNode


@pytest.fixture(scope="function")
def tmp_csv_file():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")


@pytest.fixture(scope="function", autouse=True)
def cleanup(tmp_csv_file):
    yield
    if os.path.isfile(tmp_csv_file):
        os.remove(tmp_csv_file)


@dataclasses.dataclass
class MyCustomObject:
    id: int
    integer: int
    text: str

    def __eq__(self, val) -> bool:
        return self.id == val.id and self.integer == val.integer and self.text == val.text

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))


@pytest.mark.parametrize(
    "content",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
        (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
        ([[11, 22, 33], [44, 55, 66]]),
    ],
)
def test_append(csv_file, default_data_frame, content):
    csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file})
    assert_frame_equal(csv_dn.read(), default_data_frame)

    csv_dn.append(content)
    assert_frame_equal(
        csv_dn.read(),
        pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(drop=True),
    )


def test_write_with_header_pandas(tmp_csv_file):
    csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": tmp_csv_file})

    df = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    csv_dn.write(df)
    assert pd.DataFrame.equals(csv_dn.read(), df)

    csv_dn.write(df["a"])
    assert pd.DataFrame.equals(csv_dn.read(), df[["a"]])

    series = pd.Series([1, 2, 3])
    csv_dn.write(series)
    assert np.array_equal(csv_dn.read().to_numpy(), pd.DataFrame(series).to_numpy())

    csv_dn.write(None)
    assert csv_dn.read().empty


def test_write_with_header_numpy(tmp_csv_file):
    csv_dn = CSVDataNode("bar", Scope.SCENARIO, properties={"path": tmp_csv_file, "exposed_type": "numpy"})

    arr = np.array([[1], [2], [3], [4], [5]])
    csv_dn.write(arr)
    assert np.array_equal(csv_dn.read(), arr)

    arr = arr[0:3]
    csv_dn.write(arr)
    assert np.array_equal(csv_dn.read(), arr)

    csv_dn.write(None)
    assert csv_dn.read().size == 0


def test_write_with_header_custom_exposed_type(tmp_csv_file):
    csv_dn = CSVDataNode("bar", Scope.SCENARIO, properties={"path": tmp_csv_file, "exposed_type": MyCustomObject})

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    csv_dn.write(data)
    assert all(actual == expected for actual, expected in zip(csv_dn.read(), data))

    csv_dn.write(None)
    assert csv_dn.read() == []


def test_write_without_header_pandas(tmp_csv_file):
    csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": tmp_csv_file, "has_header": False})

    df = pd.DataFrame([*zip([1, 2, 3], [4, 5, 6])])
    csv_dn.write(df)
    assert pd.DataFrame.equals(csv_dn.read(), df)

    csv_dn.write(df[0])
    assert pd.DataFrame.equals(csv_dn.read(), df[[0]])

    series = pd.Series([1, 2, 3])
    csv_dn.write(series)
    assert np.array_equal(csv_dn.read().to_numpy(), pd.DataFrame(series).to_numpy())

    csv_dn.write(None)
    assert csv_dn.read().empty


def test_write_without_header_numpy(tmp_csv_file):
    csv_dn = CSVDataNode(
        "bar", Scope.SCENARIO, properties={"path": tmp_csv_file, "exposed_type": "numpy", "has_header": False}
    )

    arr = np.array([[1], [2], [3], [4], [5]])
    csv_dn.write(arr)
    assert np.array_equal(csv_dn.read(), arr)

    arr = arr[0:3]
    csv_dn.write(arr)
    assert np.array_equal(csv_dn.read(), arr)

    csv_dn.write(None)
    assert csv_dn.read().size == 0


def test_write_without_header_custom_exposed_type(tmp_csv_file):
    csv_dn = CSVDataNode(
        "bar", Scope.SCENARIO, properties={"path": tmp_csv_file, "exposed_type": MyCustomObject, "has_header": False}
    )

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    csv_dn.write(data)
    assert all(actual == expected for actual, expected in zip(csv_dn.read(), data))

    csv_dn.write(None)
    assert csv_dn.read() == []


def test_write_with_different_encoding(csv_file):
    data = pd.DataFrame([{"≥a": 1, "b": 2}])

    utf8_dn = CSVDataNode("utf8_dn", Scope.SCENARIO, properties={"default_path": csv_file})
    utf16_dn = CSVDataNode("utf16_dn", Scope.SCENARIO, properties={"default_path": csv_file, "encoding": "utf-16"})

    # If a file is written with utf-8 encoding, it can only be read with utf-8, not utf-16 encoding
    utf8_dn.write(data)
    assert np.array_equal(utf8_dn.read(), data)
    with pytest.raises(UnicodeError):
        utf16_dn.read()

    # If a file is written with utf-16 encoding, it can only be read with utf-16, not utf-8 encoding
    utf16_dn.write(data)
    assert np.array_equal(utf16_dn.read(), data)
    with pytest.raises(UnicodeError):
        utf8_dn.read()


def test_write_with_column_names(tmp_csv_file):
    data = [[11, 22, 33], [44, 55, 66]]
    columns = ["e", "f", "g"]

    csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": tmp_csv_file})
    csv_dn.write_with_column_names(data, columns)
    df = pd.DataFrame(data, columns=columns)
    assert pd.DataFrame.equals(df, csv_dn.read())
