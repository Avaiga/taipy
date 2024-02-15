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


@pytest.fixture(scope="function")
def tmp_excel_file():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.xlsx")


@pytest.fixture(scope="function", autouse=True)
def cleanup(tmp_excel_file):
    yield
    if os.path.exists(tmp_excel_file):
        os.remove(tmp_excel_file)

@pytest.fixture(scope="function")
def tmp_excel_file_2():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp2.xlsx")


@pytest.fixture(scope="function", autouse=True)
def cleanup_2(tmp_excel_file_2):
    yield
    if os.path.exists(tmp_excel_file_2):
        os.remove(tmp_excel_file_2)


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


sheet_names = ["Sheet1", "Sheet2"]


def test_write_with_header_multiple_sheet_pandas_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "sheet_name": sheet_names})

    df_1 = pd.DataFrame([{"a": 1, "b": 2, "c": 3}])
    df_2 = pd.DataFrame([{"a": 4, "b": 5, "c": 6}])
    sheet_data = {"Sheet1": df_1, "Sheet2": df_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": df_1[["a"]], "Sheet2": df_2[["a"]]}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": pd.Series([1, 2, 3]), "Sheet2": pd.Series([4, 5, 6])}
    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name].to_numpy(), pd.DataFrame(sheet_data[sheet_name]).to_numpy())


def test_write_with_header_multiple_sheet_pandas_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file})

    df_1 = pd.DataFrame([{"a": 1, "b": 2, "c": 3}])
    df_2 = pd.DataFrame([{"a": 4, "b": 5, "c": 6}])
    sheet_data = {"Sheet1": df_1, "Sheet2": df_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": df_1[["a"]], "Sheet2": df_2[["a"]]}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": pd.Series([1, 2, 3]), "Sheet2": pd.Series([4, 5, 6])}
    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name].to_numpy(), pd.DataFrame(sheet_data[sheet_name]).to_numpy())


def test_write_with_header_multiple_sheet_numpy_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "sheet_name": sheet_names, "exposed_type": "numpy"}
    )

    arr_1 = np.array([[1], [2], [3]])
    arr_2 = np.array([[4], [5], [6]])
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])

    arr_1 = arr_1[0:1]
    arr_2 = arr_2[0:1]
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])


def test_write_with_header_multiple_sheet_numpy_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "exposed_type": "numpy"})

    arr_1 = np.array([[1], [2], [3]])
    arr_2 = np.array([[4], [5], [6]])
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])

    arr_1 = arr_1[0:1]
    arr_2 = arr_2[0:1]
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])


def test_write_with_header_multiple_sheet_custom_exposed_type_with_sheet_name(tmp_excel_file_2):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file_2, "sheet_name": sheet_names, "exposed_type": MyCustomObject},
    )
    row_1 = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    row_2 = [MyCustomObject(0, 4, "hello"), MyCustomObject(1, 5, "abc"), MyCustomObject(2, 6, ".")]
    sheet_data = {"Sheet1": row_1, "Sheet2": row_2}

    excel_dn.write(sheet_data)
    excel_dn.read()
    # assert len(excel_dn_data) == len(sheet_data) == 2
    # for sheet_name in sheet_data.keys():
    #     assert all(actual == expected for actual, expected in zip(excel_dn_data[sheet_name], sheet_data[sheet_name]))


def test_write_with_header_multiple_sheet_custom_exposed_type_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "exposed_type": MyCustomObject})

    row_1 = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    row_2 = [MyCustomObject(0, 4, "hello"), MyCustomObject(1, 5, "abc"), MyCustomObject(2, 6, ".")]
    sheet_data = {"Sheet1": row_1, "Sheet2": row_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert all(actual == expected for actual, expected in zip(excel_dn_data[sheet_name], sheet_data[sheet_name]))


def test_write_without_header_multiple_sheet_pandas_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "sheet_name": sheet_names, "has_header": False}
    )

    df_1 = pd.DataFrame([*zip([1, 2, 3])])
    df_2 = pd.DataFrame([*zip([4, 5, 6])])
    sheet_data = {"Sheet1": df_1, "Sheet2": df_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": df_1[[0]], "Sheet2": df_2[[0]]}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": pd.Series([1, 2, 3]), "Sheet2": pd.Series([4, 5, 6])}
    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name].to_numpy(), pd.DataFrame(sheet_data[sheet_name]).to_numpy())


def test_write_without_header_multiple_sheet_pandas_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": tmp_excel_file, "has_header": False})

    df_1 = pd.DataFrame([*zip([1, 2, 3])])
    df_2 = pd.DataFrame([*zip([4, 5, 6])])
    sheet_data = {"Sheet1": df_1, "Sheet2": df_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": df_1[[0]], "Sheet2": df_2[[0]]}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert pd.DataFrame.equals(excel_dn_data[sheet_name], sheet_data[sheet_name])

    sheet_data = {"Sheet1": pd.Series([1, 2, 3]), "Sheet2": pd.Series([4, 5, 6])}
    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name].to_numpy(), pd.DataFrame(sheet_data[sheet_name]).to_numpy())


def test_write_without_header_multiple_sheet_numpy_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "sheet_name": sheet_names, "exposed_type": "numpy", "has_header": False},
    )

    arr_1 = np.array([[1], [2], [3]])
    arr_2 = np.array([[4], [5], [6]])
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])

    arr_1 = arr_1[0:1]
    arr_2 = arr_2[0:1]
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])


def test_write_without_header_multiple_sheet_numpy_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "exposed_type": "numpy", "has_header": False}
    )

    arr_1 = np.array([[1], [2], [3]])
    arr_2 = np.array([[4], [5], [6]])
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])

    arr_1 = arr_1[0:1]
    arr_2 = arr_2[0:1]
    sheet_data = {"Sheet1": arr_1, "Sheet2": arr_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert np.array_equal(excel_dn_data[sheet_name], sheet_data[sheet_name])


def test_write_without_header_multiple_sheet_custom_exposed_type_with_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={
            "path": tmp_excel_file,
            "sheet_name": sheet_names,
            "exposed_type": MyCustomObject,
            "has_header": False,
        },
    )

    row_1 = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    row_2 = [MyCustomObject(0, 4, "hello"), MyCustomObject(1, 5, "abc"), MyCustomObject(2, 6, ".")]
    sheet_data = {"Sheet1": row_1, "Sheet2": row_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert all(actual == expected for actual, expected in zip(excel_dn_data[sheet_name], sheet_data[sheet_name]))


def test_write_without_header_multiple_sheet_custom_exposed_type_without_sheet_name(tmp_excel_file):
    excel_dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": tmp_excel_file, "exposed_type": MyCustomObject, "has_header": False}
    )

    row_1 = [MyCustomObject(0, 1, "hi"), MyCustomObject(1, 2, "world"), MyCustomObject(2, 3, "text")]
    row_2 = [MyCustomObject(0, 4, "hello"), MyCustomObject(1, 5, "abc"), MyCustomObject(2, 6, ".")]
    sheet_data = {"Sheet1": row_1, "Sheet2": row_2}

    excel_dn.write(sheet_data)
    excel_dn_data = excel_dn.read()
    assert len(excel_dn_data) == len(sheet_data) == 2
    for sheet_name in sheet_data.keys():
        assert all(actual == expected for actual, expected in zip(excel_dn_data[sheet_name], sheet_data[sheet_name]))


@pytest.mark.skip(reason="Not implemented on pandas 1.3.5")
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
