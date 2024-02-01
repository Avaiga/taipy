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

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.core.data.excel import ExcelDataNode
from taipy.core.exceptions.exceptions import SheetNameLengthMismatch


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.xlsx")
    if os.path.exists(path):
        os.remove(path)


class MyCustomObject:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


class MyCustomObject1:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


class MyCustomObject2:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


@pytest.mark.parametrize(
    "content,columns",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
        ([[11, 22, 33], [44, 55, 66]], None),
        ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
    ],
)
def test_write(excel_file, default_data_frame, content, columns):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1"})
    assert np.array_equal(excel_dn.read().values, default_data_frame.values)
    if not columns:
        excel_dn.write(content)
        df = pd.DataFrame(content)
    else:
        excel_dn.write_with_column_names(content, columns)
        df = pd.DataFrame(content, columns=columns)

    assert np.array_equal(excel_dn.read().values, df.values)

    excel_dn.write(None)
    assert len(excel_dn.read()) == 0


@pytest.mark.parametrize(
    "content,sheet_name",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], "sheet_name"),
        ([[11, 22, 33], [44, 55, 66]], ["sheet_name"]),
    ],
)
def test_write_with_sheet_name(excel_file_with_sheet_name, default_data_frame, content, sheet_name):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file_with_sheet_name, "sheet_name": sheet_name}
    )
    df = pd.DataFrame(content)

    if isinstance(sheet_name, str):
        assert np.array_equal(excel_dn.read().values, default_data_frame.values)
    else:
        assert np.array_equal(excel_dn.read()["sheet_name"].values, default_data_frame.values)

    excel_dn.write(content)
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


@pytest.mark.parametrize(
    "content,sheet_name",
    [
        ([[11, 22, 33], [44, 55, 66]], ["sheet_name_1", "sheet_name_2"]),
    ],
)
def test_raise_write_with_sheet_name_length_mismatch(
    excel_file_with_sheet_name, default_data_frame, content, sheet_name
):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file_with_sheet_name, "sheet_name": sheet_name}
    )
    with pytest.raises(SheetNameLengthMismatch):
        excel_dn.write(content)


@pytest.mark.parametrize(
    "content",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
    ],
)
def test_write_without_sheet_name(excel_file_with_sheet_name, default_data_frame, content):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file_with_sheet_name})
    default_data_frame = {"sheet_name": default_data_frame}
    df = {"Sheet1": pd.DataFrame(content)}

    assert np.array_equal(excel_dn.read()["sheet_name"].values, default_data_frame["sheet_name"].values)

    excel_dn.write(content)
    assert np.array_equal(excel_dn.read()["Sheet1"].values, df["Sheet1"].values)

    sheet_names = pd.ExcelFile(excel_file_with_sheet_name).sheet_names
    expected_sheet_name = "Sheet1"

    assert sheet_names[0] == expected_sheet_name

    excel_dn.write(None)
    assert len(excel_dn.read()) == 1


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


@pytest.mark.parametrize(
    "content,columns",
    [
        ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
        ([[11, 22, 33], [44, 55, 66]], None),
        ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
    ],
)
def test_write_multi_sheet(excel_file_with_multi_sheet, default_multi_sheet_data_frame, content, columns):
    sheet_names = ["Sheet1", "Sheet2"]

    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": excel_file_with_multi_sheet, "sheet_name": sheet_names},
    )

    for sheet_name in sheet_names:
        assert np.array_equal(excel_dn.read()[sheet_name].values, default_multi_sheet_data_frame[sheet_name].values)

    multi_sheet_content = {sheet_name: pd.DataFrame(content) for sheet_name in sheet_names}

    excel_dn.write(multi_sheet_content)

    for sheet_name in sheet_names:
        assert np.array_equal(excel_dn.read()[sheet_name].values, multi_sheet_content[sheet_name].values)


def test_write_multi_sheet_numpy(excel_file_with_multi_sheet):
    sheet_names = ["Sheet1", "Sheet2"]

    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": excel_file_with_multi_sheet, "sheet_name": sheet_names, "exposed_type": "numpy"},
    )

    sheets_data = [[11, 22, 33], [44, 55, 66]]
    data = {sheet_name: pd.DataFrame(sheet_data).to_numpy() for sheet_name, sheet_data in zip(sheet_names, sheets_data)}
    excel_dn.write(data)
    read_data = excel_dn.read()
    assert all(np.array_equal(data[sheet_name], read_data[sheet_name]) for sheet_name in sheet_names)


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


@pytest.mark.parametrize(
    "content",
    [
        (
            {
                "Sheet1": pd.DataFrame([{"a": 11, "b": 22, "c": 33}]),
                "Sheet2": pd.DataFrame([{"a": 44, "b": 55, "c": 66}]),
            }
        ),
        (
            {
                "Sheet1": pd.DataFrame({"a": [11, 44], "b": [22, 55], "c": [33, 66]}),
                "Sheet2": pd.DataFrame([{"a": 77, "b": 88, "c": 99}]),
            }
        ),
        ({"Sheet1": np.array([[11, 22, 33], [44, 55, 66]]), "Sheet2": np.array([[77, 88, 99]])}),
    ],
)
def test_append_pandas_multisheet(excel_file_with_multi_sheet, default_multi_sheet_data_frame, content):
    dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file_with_multi_sheet, "sheet_name": ["Sheet1", "Sheet2"]}
    )
    assert_frame_equal(dn.read()["Sheet1"], default_multi_sheet_data_frame["Sheet1"])
    assert_frame_equal(dn.read()["Sheet2"], default_multi_sheet_data_frame["Sheet2"])

    dn.append(content)

    assert_frame_equal(
        dn.read()["Sheet1"],
        pd.concat(
            [default_multi_sheet_data_frame["Sheet1"], pd.DataFrame(content["Sheet1"], columns=["a", "b", "c"])]
        ).reset_index(drop=True),
    )
    assert_frame_equal(
        dn.read()["Sheet2"],
        pd.concat(
            [default_multi_sheet_data_frame["Sheet2"], pd.DataFrame(content["Sheet2"], columns=["a", "b", "c"])]
        ).reset_index(drop=True),
    )


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
