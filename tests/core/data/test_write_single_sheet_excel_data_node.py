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

from taipy.config.common.scope import Scope
from taipy.core.data.excel import ExcelDataNode
from taipy.core.exceptions.exceptions import SheetNameLengthMismatch


@pytest.fixture(scope="function")
def tmp_excel_file():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.xlsx")


@pytest.fixture(scope="function", autouse=True)
def cleanup(tmp_excel_file):
    yield
    if os.path.exists(tmp_excel_file):
        os.remove(tmp_excel_file)


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


def test_write_with_header_single_sheet_pandas_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "sheet_name": "Sheet1"})

    df = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])

    excel_dn.write(df)
    assert pd.DataFrame.equals(excel_dn.read(), df)

    excel_dn.write(None)
    assert len(excel_dn.read()) == 0

    excel_dn.write(df["a"])
    assert pd.DataFrame.equals(excel_dn.read(), df[["a"]])

    series = pd.Series([1, 2, 3])
    excel_dn.write(series)
    assert np.array_equal(excel_dn.read().to_numpy(), pd.DataFrame(series).to_numpy())

    excel_dn.write(None)
    assert excel_dn.read().empty


def test_write_with_header_single_sheet_pandas_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file})

    df = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])

    excel_dn.write(df)
    excel_data = excel_dn.read()

    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert pd.DataFrame.equals(excel_data["Sheet1"], df)

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert len(excel_dn.read()["Sheet1"]) == 0

    excel_dn.write(df["a"])
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert pd.DataFrame.equals(excel_dn.read()["Sheet1"], df[["a"]])

    series = pd.Series([1, 2, 3])
    excel_dn.write(series)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"].to_numpy(), pd.DataFrame(series).to_numpy())

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert excel_dn.read()["Sheet1"].empty


def test_write_without_header_single_sheet_pandas_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "sheet_name": "Sheet1", "has_header": False}
    )

    df = pd.DataFrame([*zip([1, 2, 3], [4, 5, 6])])

    excel_dn.write(df)
    assert pd.DataFrame.equals(excel_dn.read(), df)

    excel_dn.write(None)
    assert len(excel_dn.read()) == 0

    excel_dn.write(df[0])
    assert pd.DataFrame.equals(excel_dn.read(), df[[0]])

    series = pd.Series([1, 2, 3])
    excel_dn.write(series)
    assert np.array_equal(excel_dn.read().to_numpy(), pd.DataFrame(series).to_numpy())

    excel_dn.write(None)
    assert excel_dn.read().empty


def test_write_without_header_single_sheet_pandas_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "has_header": False})

    df = pd.DataFrame([*zip([1, 2, 3], [4, 5, 6])])

    excel_dn.write(df)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert pd.DataFrame.equals(excel_data["Sheet1"], df)

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert len(excel_dn.read()["Sheet1"]) == 0

    excel_dn.write(df[0])
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert pd.DataFrame.equals(excel_dn.read()["Sheet1"], df[[0]])

    series = pd.Series([1, 2, 3])
    excel_dn.write(series)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"].to_numpy(), pd.DataFrame(series).to_numpy())

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert excel_dn.read()["Sheet1"].empty


def test_write_with_header_single_sheet_numpy_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "sheet_name": "Sheet1", "exposed_type": "numpy"}
    )

    arr = np.array([[1], [2], [3], [4], [5]])
    excel_dn.write(arr)
    assert np.array_equal(excel_dn.read(), arr)

    arr = arr[0:3]
    excel_dn.write(arr)
    assert np.array_equal(excel_dn.read(), arr)

    excel_dn.write(None)
    assert excel_dn.read().size == 0


def test_write_with_header_single_sheet_numpy_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "exposed_type": "numpy"})

    arr = np.array([[1], [2], [3], [4], [5]])
    excel_dn.write(arr)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"], arr)

    arr = arr[0:3]
    excel_dn.write(arr)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"], arr)

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert excel_dn.read()["Sheet1"].size == 0


def test_write_without_header_single_sheet_numpy_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "sheet_name": "Sheet1", "exposed_type": "numpy", "has_header": False},
    )

    arr = np.array([[1], [2], [3], [4], [5]])
    excel_dn.write(arr)
    assert np.array_equal(excel_dn.read(), arr)

    arr = arr[0:3]
    excel_dn.write(arr)
    assert np.array_equal(excel_dn.read(), arr)

    excel_dn.write(None)
    assert excel_dn.read().size == 0


def test_write_without_header_single_sheet_numpy_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "exposed_type": "numpy", "has_header": False}
    )

    arr = np.array([[1], [2], [3], [4], [5]])
    excel_dn.write(arr)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"], arr)

    arr = arr[0:3]
    excel_dn.write(arr)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert np.array_equal(excel_dn.read()["Sheet1"], arr)

    excel_dn.write(None)
    excel_data = excel_dn.read()
    assert isinstance(excel_data, dict) and "Sheet1" in excel_data.keys()
    assert excel_dn.read()["Sheet1"].size == 0


def test_write_with_header_single_sheet_custom_exposed_type_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "sheet_name": "Sheet1", "exposed_type": MyCustomObject},
    )

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    excel_dn.write(data)
    assert all(actual == expected for actual, expected in zip(excel_dn.read(), data))

    excel_dn.write(None)
    assert excel_dn.read() == []


def test_write_with_header_single_sheet_custom_exposed_type_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "exposed_type": MyCustomObject})

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    excel_dn.write(data)
    assert all(actual == expected for actual, expected in zip(excel_dn.read(), data))

    excel_dn.write(None)
    assert excel_dn.read() == []


def test_write_without_header_single_sheet_custom_exposed_type_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={
            "path": tmp_excel_file,
            "sheet_name": "Sheet1",
            "exposed_type": MyCustomObject,
            "has_header": False,
        },
    )

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    excel_dn.write(data)
    assert all(actual == expected for actual, expected in zip(excel_dn.read(), data))

    excel_dn.write(None)
    assert excel_dn.read() == []


def test_write_without_header_single_sheet_custom_exposed_type_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "exposed_type": MyCustomObject, "has_header": False}
    )

    data = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    excel_dn.write(data)
    assert all(actual == expected for actual, expected in zip(excel_dn.read(), data))

    excel_dn.write(None)
    assert excel_dn.read() == []


def test_raise_write_with_sheet_name_length_mismatch(excel_file_with_sheet_name):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": excel_file_with_sheet_name, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
    )
    with pytest.raises(SheetNameLengthMismatch):
        excel_dn.write([])


@pytest.mark.parametrize(
    "content,columns,sheet_name",
    [
        ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"], "sheet_name"),
        ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"], ["sheet_name"]),
    ],
)
def test_write_with_column_and_sheet_name(excel_file_with_sheet_name, default_data_frame, content, columns, sheet_name):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file_with_sheet_name, "sheet_name": sheet_name}
    )
    df = pd.DataFrame(content)

    if isinstance(sheet_name, str):
        assert np.array_equal(excel_dn.read().values, default_data_frame.values)
    else:
        assert np.array_equal(excel_dn.read()["sheet_name"].values, default_data_frame.values)

    excel_dn.write_with_column_names(content, columns)

    if isinstance(sheet_name, str):
        assert np.array_equal(excel_dn.read().values, df.values)
    else:
        assert np.array_equal(excel_dn.read()["sheet_name"].values, df.values)

    sheet_names = pd.ExcelFile(excel_file_with_sheet_name).sheet_names
    expected_sheet_name = sheet_name[0] if isinstance(sheet_name, list) else sheet_name

    assert sheet_names[0] == expected_sheet_name

    excel_dn.write(None)
    if isinstance(sheet_name, str):
        assert len(excel_dn.read()) == 0
    else:
        assert len(excel_dn.read()) == 1


@pytest.mark.skip(reason="Not implemented on pandas 1.3.5")
@pytest.mark.parametrize(
    "content",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
        (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
        ([[11, 22, 33], [44, 55, 66]]),
    ],
)
def test_append_pandas_with_sheetname(excel_file, default_data_frame, content):
    dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1"})
    assert_frame_equal(dn.read(), default_data_frame)

    dn.append(content)
    assert_frame_equal(
        dn.read(),
        pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(drop=True),
    )


@pytest.mark.skip(reason="Not implemented on pandas 1.3.5")
@pytest.mark.parametrize(
    "content",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
        (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
        ([[11, 22, 33], [44, 55, 66]]),
    ],
)
def test_append_pandas_without_sheetname(excel_file, default_data_frame, content):
    dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file})
    assert_frame_equal(dn.read()["Sheet1"], default_data_frame)

    dn.append(content)
    assert_frame_equal(
        dn.read()["Sheet1"],
        pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(drop=True),
    )


@pytest.mark.skip(reason="Not implemented on pandas 1.3.5")
@pytest.mark.parametrize(
    "content",
    [
        ({"Sheet1": pd.DataFrame([{"a": 11, "b": 22, "c": 33}])}),
        (pd.DataFrame({"a": [11, 44], "b": [22, 55], "c": [33, 66]})),
        ([[11, 22, 33], [44, 55, 66]]),
    ],
)
def test_append_only_first_sheet_of_a_multisheet_file(
    excel_file_with_multi_sheet, default_multi_sheet_data_frame, content
):
    dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file_with_multi_sheet, "sheet_name": ["Sheet1", "Sheet2"]}
    )
    assert_frame_equal(dn.read()["Sheet1"], default_multi_sheet_data_frame["Sheet1"])
    assert_frame_equal(dn.read()["Sheet2"], default_multi_sheet_data_frame["Sheet2"])

    dn.append(content)

    appended_content = content["Sheet1"] if isinstance(content, dict) else content
    assert_frame_equal(
        dn.read()["Sheet1"],
        pd.concat(
            [default_multi_sheet_data_frame["Sheet1"], pd.DataFrame(appended_content, columns=["a", "b", "c"])]
        ).reset_index(drop=True),
    )
    assert_frame_equal(dn.read()["Sheet2"], default_multi_sheet_data_frame["Sheet2"])
