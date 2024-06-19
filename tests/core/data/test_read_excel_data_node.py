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
from typing import Dict

import numpy as np
import pandas as pd
import polars as pl
import pytest

from taipy.config.common.scope import Scope
from taipy.core.data.excel import ExcelDataNode
from taipy.core.exceptions.exceptions import (
    ExposedTypeLengthMismatch,
    NoData,
    NonExistingExcelSheet,
)


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


excel_file_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
sheet_names = ["Sheet1", "Sheet2"]
custom_class_dict = {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}


def test_raise_no_data_with_header():
    with pytest.raises(NoData):
        not_existing_excel = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.xlsx"})
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()


def test_read_empty_excel_with_header():
    empty_excel_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/empty.xlsx")
    empty_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": empty_excel_path, "exposed_type": MyCustomObject},
    )
    assert len(empty_excel.read()) == 1


def test_raise_no_data_without_header():
    with pytest.raises(NoData):
        not_existing_excel = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": "WRONG.xlsx", "has_header": False}
        )
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()


def test_read_empty_excel_without_header():
    empty_excel_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/empty.xlsx")
    empty_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": empty_excel_path, "exposed_type": MyCustomObject, "has_header": False},
    )
    assert len(empty_excel.read()) == 1


def test_read_multi_sheet_with_header_no_data():
    not_existing_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": "WRONG.xlsx", "sheet_name": ["sheet_name_1", "sheet_name_2"]},
    )
    with pytest.raises(NoData):
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()


def test_read_multi_sheet_without_header_no_data():
    not_existing_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": "WRONG.xlsx", "has_header": False, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
    )
    with pytest.raises(NoData):
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()


########################## SINGLE SHEET ##########################


def test_read_single_sheet_with_header_no_existing_sheet():
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "sheet_name": "abc", "exposed_type": MyCustomObject},
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()


def test_read_single_sheet_without_header_no_existing_sheet():
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "sheet_name": "abc", "exposed_type": MyCustomObject},
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()


def test_read_with_header_pandas():
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "sheet_name": "Sheet1"}
    )

    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 5
    assert pd.DataFrame.equals(data_pandas, pd.read_excel(excel_file_path))


def test_read_with_header_numpy():
    excel_data_node_as_numpy = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "exposed_type": "numpy", "sheet_name": "Sheet1"}
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 5
    assert np.array_equal(data_numpy, pd.read_excel(excel_file_path).to_numpy())


def test_read_with_header_polars():
    excel_data_node_as_polars = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "sheet_name": "Sheet1", "exposed_type": "polars"}
    )

    data_polars = excel_data_node_as_polars.read()
    assert isinstance(data_polars, pl.DataFrame)
    assert len(data_polars) == 5
    assert pl.DataFrame.equals(data_polars, pl.read_excel(excel_file_path, engine="openpyxl"))


def test_read_with_header_custom_exposed_type():
    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "exposed_type": MyCustomObject, "sheet_name": "Sheet1"},
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 5

    data_pandas = pd.read_excel(excel_file_path)
    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas["id"] == row_custom.id
        assert row_pandas["integer"] == row_custom.integer
        assert row_pandas["text"] == row_custom.text


def test_read_without_header_pandas():
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False, "sheet_name": "Sheet1"}
    )
    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 6
    assert pd.DataFrame.equals(data_pandas, pd.read_excel(excel_file_path, header=None))


def test_read_without_header_numpy():
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "exposed_type": "numpy", "sheet_name": "Sheet1"},
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 6
    assert np.array_equal(data_numpy, pd.read_excel(excel_file_path, header=None).to_numpy())


# def test_read_without_header_polars():
#     excel_data_node_as_polars = ExcelDataNode(
#         "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False, "sheet_name": "Sheet1", "exposed_type": "polars"}
#     )
#     data_polars = excel_data_node_as_polars.read()
#     assert isinstance(data_polars, pl.DataFrame)
#     assert len(data_polars) == 6
#     assert pl.DataFrame.equals(data_polars, pl.read_excel(excel_file_path, engine="openpyxl", read_options={"has_header": False}))


def test_read_without_header_exposed_custom_type():
    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "has_header": False,
            "exposed_type": MyCustomObject,
            "sheet_name": "Sheet1",
        },
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 6

    data_pandas = pd.read_excel(excel_file_path, header=None)
    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas[0] == row_custom.id
        assert row_pandas[1] == row_custom.integer
        assert row_pandas[2] == row_custom.text


########################## MULTI SHEET ##########################


def test_read_multi_sheet_with_header_no_existing_sheet():
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "sheet_name": ["Sheet1", "xyz"],
            "exposed_type": MyCustomObject1,
        },
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()


def test_read_multi_sheet_without_header_no_existing_sheet():
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "has_header": False,
            "sheet_name": ["Sheet1", "xyz"],
            "exposed_type": MyCustomObject1,
        },
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()


def test_raise_exposed_type_length_mismatch_with_header():
    with pytest.raises(ExposedTypeLengthMismatch):
        dn = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={
                "path": excel_file_path,
                "sheet_name": ["Sheet1"],
                "exposed_type": [MyCustomObject1, MyCustomObject2],
            },
        )
        dn.read()


def test_raise_exposed_type_length_mismatch_without_header():
    with pytest.raises(ExposedTypeLengthMismatch):
        dn = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={
                "path": excel_file_path,
                "sheet_name": ["Sheet1"],
                "exposed_type": [MyCustomObject1, MyCustomObject2],
                "has_header": False,
            },
        )
        dn.read()


def test_read_multi_sheet_with_header_pandas():
    # With sheet name
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "sheet_name": sheet_names}
    )

    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, Dict)
    assert len(data_pandas) == 2
    assert all(
        len(data_pandas[sheet_name]) == 5 and isinstance(data_pandas[sheet_name], pd.DataFrame)
        for sheet_name in sheet_names
    )
    assert list(data_pandas.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert pd.DataFrame.equals(data_pandas[sheet_name], pd.read_excel(excel_file_path, sheet_name=sheet_name))

    # Without sheet name
    excel_data_node_as_pandas_no_sheet_name = ExcelDataNode("bar", Scope.SCENARIO, properties={"path": excel_file_path})

    data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
    assert isinstance(data_pandas_no_sheet_name, Dict)
    for key in data_pandas_no_sheet_name.keys():
        assert isinstance(data_pandas_no_sheet_name[key], pd.DataFrame)
        assert data_pandas[key].equals(data_pandas_no_sheet_name[key])


def test_read_multi_sheet_with_header_numpy():
    data_pandas = pd.read_excel(excel_file_path, sheet_name=sheet_names)

    # With sheet name
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "sheet_name": sheet_names, "exposed_type": "numpy"},
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, Dict)
    assert len(data_numpy) == 2
    assert all(
        len(data_numpy[sheet_name]) == 5 and isinstance(data_numpy[sheet_name], np.ndarray)
        for sheet_name in sheet_names
    )
    assert list(data_numpy.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert np.array_equal(data_pandas[sheet_name], pd.read_excel(excel_file_path, sheet_name=sheet_name).to_numpy())

    # Without sheet name
    excel_data_node_as_numpy_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "exposed_type": "numpy"},
    )

    data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
    assert isinstance(data_numpy_no_sheet_name, Dict)
    for key in data_numpy_no_sheet_name.keys():
        assert isinstance(data_numpy_no_sheet_name[key], np.ndarray)
        assert np.array_equal(data_numpy[key], data_numpy_no_sheet_name[key])


def test_read_multi_sheet_with_header_polars():
    # With sheet name
    excel_data_node_as_polars = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "sheet_name": sheet_names, "exposed_type": "polars"}
    )

    data_polars = excel_data_node_as_polars.read()
    assert isinstance(data_polars, Dict)
    assert len(data_polars) == 2
    assert all(
        len(data_polars[sheet_name]) == 5 and isinstance(data_polars[sheet_name], pl.DataFrame)
        for sheet_name in sheet_names
    )
    assert list(data_polars.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert pl.DataFrame.equals(
            data_polars[sheet_name], pl.read_excel(excel_file_path, sheet_name=sheet_name, engine="openpyxl")
        )

    # Without sheet name
    excel_data_node_as_polars_no_sheet_name = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "exposed_type": "polars"}
    )

    data_polars_no_sheet_name = excel_data_node_as_polars_no_sheet_name.read()
    assert isinstance(data_polars_no_sheet_name, Dict)
    for key in data_polars_no_sheet_name.keys():
        assert isinstance(data_polars_no_sheet_name[key], pl.DataFrame)
        assert data_polars[key].equals(data_polars_no_sheet_name[key])


def test_read_multi_sheet_with_header_single_custom_exposed_type():
    data_pandas = pd.read_excel(excel_file_path, sheet_name=sheet_names)

    # With sheet name
    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "sheet_name": sheet_names, "exposed_type": MyCustomObject1},
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert isinstance(data_custom, Dict)
    assert len(data_custom) == 2
    assert all(len(data_custom[sheet_name]) == 5 for sheet_name in sheet_names)
    assert list(data_custom.keys()) == sheet_names

    for sheet_name in sheet_names:
        sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], data_custom[sheet_name]
        for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
            assert isinstance(row_custom, MyCustomObject1)
            assert row_pandas["id"] == row_custom.id
            assert row_pandas["integer"] == row_custom.integer
            assert row_pandas["text"] == row_custom.text

    # Without sheet name
    excel_data_node_as_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "exposed_type": MyCustomObject1},
    )

    data_custom_no_sheet_name = excel_data_node_as_custom_object_no_sheet_name.read()
    assert isinstance(data_custom_no_sheet_name, Dict)
    assert len(data_custom_no_sheet_name) == 2
    assert data_custom.keys() == data_custom_no_sheet_name.keys()

    for sheet_name in sheet_names:
        sheet_data_custom_no_sheet_name, sheet_data_custom = (
            data_custom_no_sheet_name[sheet_name],
            data_custom[sheet_name],
        )
        for row_custom_no_sheet_name, row_custom in zip(sheet_data_custom_no_sheet_name, sheet_data_custom):
            assert isinstance(row_custom_no_sheet_name, MyCustomObject1)
            assert row_custom_no_sheet_name.id == row_custom.id
            assert row_custom_no_sheet_name.integer == row_custom.integer
            assert row_custom_no_sheet_name.text == row_custom.text


def test_read_multi_sheet_with_header_multiple_custom_exposed_type():
    data_pandas = pd.read_excel(excel_file_path, sheet_name=sheet_names)

    # With sheet name
    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "sheet_name": sheet_names, "exposed_type": custom_class_dict},
    )
    assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "sheet_name": sheet_names,
            "exposed_type": [MyCustomObject1, MyCustomObject2],
        },
    )
    assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == [MyCustomObject1, MyCustomObject2]

    multi_data_custom = excel_data_node_as_multi_custom_object.read()
    assert isinstance(multi_data_custom, Dict)
    assert len(multi_data_custom) == 2
    assert all(len(multi_data_custom[sheet_name]) == 5 for sheet_name in sheet_names)
    assert list(multi_data_custom.keys()) == sheet_names

    for sheet_name, custom_class in custom_class_dict.items():
        sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], multi_data_custom[sheet_name]
        for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
            assert isinstance(row_custom, custom_class)
            assert row_pandas["id"] == row_custom.id
            assert row_pandas["integer"] == row_custom.integer
            assert row_pandas["text"] == row_custom.text

    # Without sheet name
    excel_data_node_as_multi_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "exposed_type": custom_class_dict},
    )
    assert excel_data_node_as_multi_custom_object_no_sheet_name.properties["exposed_type"] == custom_class_dict

    multi_data_custom_no_sheet_name = excel_data_node_as_multi_custom_object_no_sheet_name.read()
    assert isinstance(multi_data_custom_no_sheet_name, Dict)
    assert len(multi_data_custom_no_sheet_name) == 2
    assert multi_data_custom.keys() == multi_data_custom_no_sheet_name.keys()

    for sheet_name, custom_class in custom_class_dict.items():
        sheet_data_custom_no_sheet_name, sheet_data_custom = (
            multi_data_custom_no_sheet_name[sheet_name],
            multi_data_custom[sheet_name],
        )
        for row_custom_no_sheet_name, row_custom in zip(sheet_data_custom_no_sheet_name, sheet_data_custom):
            assert isinstance(row_custom_no_sheet_name, custom_class)
            assert row_custom_no_sheet_name.id == row_custom.id
            assert row_custom_no_sheet_name.integer == row_custom.integer
            assert row_custom_no_sheet_name.text == row_custom.text


def test_read_multi_sheet_without_header_pandas():
    # With sheet name
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False, "sheet_name": sheet_names}
    )
    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, Dict)
    assert len(data_pandas) == 2
    assert all(len(data_pandas[sheet_name]) == 6 for sheet_name in sheet_names)
    assert list(data_pandas.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert isinstance(data_pandas[sheet_name], pd.DataFrame)
        assert pd.DataFrame.equals(
            data_pandas[sheet_name], pd.read_excel(excel_file_path, header=None, sheet_name=sheet_name)
        )

    # Without sheet name
    excel_data_node_as_pandas_no_sheet_name = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False}
    )
    data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
    assert isinstance(data_pandas_no_sheet_name, Dict)
    for key in data_pandas_no_sheet_name.keys():
        assert isinstance(data_pandas_no_sheet_name[key], pd.DataFrame)
        assert pd.DataFrame.equals(data_pandas[key], data_pandas_no_sheet_name[key])


def test_read_multi_sheet_without_header_numpy():
    data_pandas = pd.read_excel(excel_file_path, header=None, sheet_name=sheet_names)

    # With sheet name
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "sheet_name": sheet_names, "exposed_type": "numpy"},
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, Dict)
    assert len(data_numpy) == 2
    assert all(
        len(data_numpy[sheet_name] == 6) and isinstance(data_numpy[sheet_name], np.ndarray)
        for sheet_name in sheet_names
    )
    assert list(data_numpy.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert np.array_equal(
            data_pandas[sheet_name], pd.read_excel(excel_file_path, header=None, sheet_name=sheet_name).to_numpy()
        )

    # Without sheet name
    excel_data_node_as_numpy_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "exposed_type": "numpy"},
    )

    data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
    assert isinstance(data_numpy_no_sheet_name, Dict)
    for key in data_numpy_no_sheet_name.keys():
        assert isinstance(data_numpy_no_sheet_name[key], np.ndarray)
        assert np.array_equal(data_numpy[key], data_numpy_no_sheet_name[key])


# def test_read_multi_sheet_without_header_polars():
#     # With sheet name
#     excel_data_node_as_polars = ExcelDataNode(
#         "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False, "sheet_name": sheet_names, "exposed_type": "polars"}
#     )
#     data_polars = excel_data_node_as_polars.read()
#     assert isinstance(data_polars, Dict)
#     assert len(data_polars) == 2
#     assert all(len(data_polars[sheet_name]) == 6 for sheet_name in sheet_names)
#     assert list(data_polars.keys()) == sheet_names
#     for sheet_name in sheet_names:
#         assert isinstance(data_polars[sheet_name], pl.DataFrame)
#         assert pl.DataFrame.equals(
#             data_polars[sheet_name], pd.read_excel(excel_file_path, header=None, sheet_name=sheet_name, engine="openpyxl")
#         )

#     # Without sheet name
#     excel_data_node_as_pandas_no_sheet_name = ExcelDataNode(
#         "bar", Scope.SCENARIO, properties={"path": excel_file_path, "has_header": False, "exposed_type": "polars"}
#     )
#     data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
#     assert isinstance(data_pandas_no_sheet_name, Dict)
#     for key in data_pandas_no_sheet_name.keys():
#         assert isinstance(data_pandas_no_sheet_name[key], pl.DataFrame)
#         assert pl.DataFrame.equals(data_polars[key], data_pandas_no_sheet_name[key])


def test_read_multi_sheet_without_header_single_custom_exposed_type():
    data_pandas = pd.read_excel(excel_file_path, header=None, sheet_name=sheet_names)

    # With sheet name
    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "has_header": False,
            "sheet_name": sheet_names,
            "exposed_type": MyCustomObject1,
        },
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert excel_data_node_as_custom_object.exposed_type == MyCustomObject1
    assert isinstance(data_custom, Dict)
    assert len(data_custom) == 2
    assert all(len(data_custom[sheet_name]) == 6 for sheet_name in sheet_names)
    assert list(data_custom.keys()) == sheet_names

    for sheet_name in sheet_names:
        sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], data_custom[sheet_name]
        for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
            assert isinstance(row_custom, MyCustomObject1)
            assert row_pandas[0] == row_custom.id
            assert row_pandas[1] == row_custom.integer
            assert row_pandas[2] == row_custom.text

    # Without sheet name
    excel_data_node_as_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "exposed_type": MyCustomObject1},
    )

    data_custom_no_sheet_name = excel_data_node_as_custom_object_no_sheet_name.read()
    assert isinstance(data_custom_no_sheet_name, Dict)
    assert len(data_custom_no_sheet_name) == 2
    assert data_custom.keys() == data_custom_no_sheet_name.keys()

    for sheet_name in sheet_names:
        sheet_data_custom_no_sheet_name, sheet_data_custom = (
            data_custom_no_sheet_name[sheet_name],
            data_custom[sheet_name],
        )
        for row_custom_no_sheet_name, row_custom in zip(sheet_data_custom_no_sheet_name, sheet_data_custom):
            assert isinstance(row_custom_no_sheet_name, MyCustomObject1)
            assert row_custom_no_sheet_name.id == row_custom.id
            assert row_custom_no_sheet_name.integer == row_custom.integer
            assert row_custom_no_sheet_name.text == row_custom.text


def test_read_multi_sheet_without_header_multiple_custom_exposed_type():
    data_pandas = pd.read_excel(excel_file_path, header=None, sheet_name=sheet_names)

    # With sheet names
    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "sheet_name": sheet_names,
            "exposed_type": custom_class_dict,
            "has_header": False,
        },
    )
    assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": excel_file_path,
            "sheet_name": sheet_names,
            "exposed_type": [MyCustomObject1, MyCustomObject2],
            "has_header": False,
        },
    )
    assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == [MyCustomObject1, MyCustomObject2]

    multi_data_custom = excel_data_node_as_multi_custom_object.read()
    assert isinstance(multi_data_custom, Dict)
    assert len(multi_data_custom) == 2
    assert all(len(multi_data_custom[sheet_name]) == 6 for sheet_name in sheet_names)
    assert list(multi_data_custom.keys()) == sheet_names

    for sheet_name, custom_class in custom_class_dict.items():
        sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], multi_data_custom[sheet_name]
        for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
            assert isinstance(row_custom, custom_class)
            assert row_pandas[0] == row_custom.id
            assert row_pandas[1] == row_custom.integer
            assert row_pandas[2] == row_custom.text

    # Without sheet names
    excel_data_node_as_multi_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": excel_file_path, "has_header": False, "exposed_type": custom_class_dict},
    )

    multi_data_custom_no_sheet_name = excel_data_node_as_multi_custom_object_no_sheet_name.read()
    assert isinstance(multi_data_custom_no_sheet_name, Dict)
    assert len(multi_data_custom_no_sheet_name) == 2
    assert multi_data_custom.keys() == multi_data_custom_no_sheet_name.keys()

    for sheet_name, custom_class in custom_class_dict.items():
        sheet_data_custom_no_sheet_name, sheet_data_custom = (
            multi_data_custom_no_sheet_name[sheet_name],
            multi_data_custom[sheet_name],
        )
        for row_custom_no_sheet_name, row_custom in zip(sheet_data_custom_no_sheet_name, sheet_data_custom):
            assert isinstance(row_custom_no_sheet_name, custom_class)
            assert row_custom_no_sheet_name.id == row_custom.id
            assert row_custom_no_sheet_name.integer == row_custom.integer
            assert row_custom_no_sheet_name.text == row_custom.text
