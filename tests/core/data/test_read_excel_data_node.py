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


def test_read_with_header():
    with pytest.raises(NoData):
        not_existing_excel = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.xlsx"})
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()

    empty_excel_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/empty.xlsx")
    empty_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": empty_excel_path, "exposed_type": MyCustomObject, "has_header": True},
    )
    assert len(empty_excel.read()) == 0

    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

    # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
    excel_data_node_as_pandas = ExcelDataNode("bar", Scope.SCENARIO, properties={"path": path, "sheet_name": "Sheet1"})

    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 5
    assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path).to_numpy())

    # Create ExcelDataNode with numpy exposed_type
    excel_data_node_as_numpy = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": path, "exposed_type": "numpy", "sheet_name": "Sheet1"}
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 5
    assert np.array_equal(data_numpy, pd.read_excel(path).to_numpy())

    # Create the same ExcelDataNode but with custom exposed_type
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "sheet_name": "abc", "exposed_type": MyCustomObject},
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()

    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "exposed_type": MyCustomObject, "sheet_name": "Sheet1"},
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 5

    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas["id"] == row_custom.id
        assert row_pandas["integer"] == row_custom.integer
        assert row_pandas["text"] == row_custom.text


def test_read_without_header():
    not_existing_excel = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.xlsx", "has_header": False})
    with pytest.raises(NoData):
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()

    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

    # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "sheet_name": "Sheet1"}
    )
    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 6
    assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path, header=None).to_numpy())

    # Create ExcelDataNode with numpy exposed_type
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "exposed_type": "numpy", "sheet_name": "Sheet1"},
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 6
    assert np.array_equal(data_numpy, pd.read_excel(path, header=None).to_numpy())

    # Create the same ExcelDataNode but with custom exposed_type
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "sheet_name": "abc", "exposed_type": MyCustomObject},
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()

    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": path,
            "has_header": False,
            "exposed_type": MyCustomObject,
            "sheet_name": "Sheet1",
        },
    )

    data_custom = excel_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 6

    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas[0] == row_custom.id
        assert row_pandas[1] == row_custom.integer
        assert row_pandas[2] == row_custom.text


def test_read_multi_sheet_with_header():
    not_existing_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": "WRONG.xlsx", "sheet_name": ["sheet_name_1", "sheet_name_2"]},
    )
    with pytest.raises(NoData):
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()

    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
    sheet_names = ["Sheet1", "Sheet2"]

    # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": path, "sheet_name": sheet_names}
    )

    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, Dict)
    assert len(data_pandas) == 2
    assert all(
        len(data_pandas[sheet_name] == 5) and isinstance(data_pandas[sheet_name], pd.DataFrame)
        for sheet_name in sheet_names
    )
    assert list(data_pandas.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert data_pandas[sheet_name].equals(pd.read_excel(path, sheet_name=sheet_name))

    excel_data_node_as_pandas_no_sheet_name = ExcelDataNode("bar", Scope.SCENARIO, properties={"path": path})

    data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
    assert isinstance(data_pandas_no_sheet_name, Dict)
    for key in data_pandas_no_sheet_name.keys():
        assert isinstance(data_pandas_no_sheet_name[key], pd.DataFrame)
        assert data_pandas[key].equals(data_pandas_no_sheet_name[key])

    # Create ExcelDataNode with numpy exposed_type
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "sheet_name": sheet_names, "exposed_type": "numpy"},
    )

    data_numpy = excel_data_node_as_numpy.read()
    assert isinstance(data_numpy, Dict)
    assert len(data_numpy) == 2
    assert all(
        len(data_numpy[sheet_name] == 5) and isinstance(data_numpy[sheet_name], np.ndarray)
        for sheet_name in sheet_names
    )
    assert list(data_numpy.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert np.array_equal(data_pandas[sheet_name], pd.read_excel(path, sheet_name=sheet_name).to_numpy())

    excel_data_node_as_numpy_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "exposed_type": "numpy"},
    )

    data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
    assert isinstance(data_numpy_no_sheet_name, Dict)
    for key in data_numpy_no_sheet_name.keys():
        assert isinstance(data_numpy_no_sheet_name[key], np.ndarray)
        assert np.array_equal(data_numpy[key], data_numpy_no_sheet_name[key])

    # Create the same ExcelDataNode but with custom exposed_type
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": path,
            "sheet_name": ["Sheet1", "xyz"],
            "exposed_type": MyCustomObject1,
        },
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()

    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "sheet_name": sheet_names, "exposed_type": MyCustomObject1},
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

    excel_data_node_as_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "exposed_type": MyCustomObject1},
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

    with pytest.raises(ExposedTypeLengthMismatch):
        dn = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={
                "path": path,
                "sheet_name": ["Sheet1"],
                "exposed_type": [MyCustomObject1, MyCustomObject2],
            },
        )
        dn.read()

    custom_class_dict = {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "sheet_name": sheet_names, "exposed_type": custom_class_dict},
    )
    assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "sheet_name": sheet_names, "exposed_type": [MyCustomObject1, MyCustomObject2]},
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

    excel_data_node_as_multi_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "exposed_type": custom_class_dict},
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


def test_read_multi_sheet_without_header():
    not_existing_excel = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": "WRONG.xlsx", "has_header": False, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
    )
    with pytest.raises(NoData):
        assert not_existing_excel.read() is None
        not_existing_excel.read_or_raise()

    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
    sheet_names = ["Sheet1", "Sheet2"]

    # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
    excel_data_node_as_pandas = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "sheet_name": sheet_names}
    )
    data_pandas = excel_data_node_as_pandas.read()
    assert isinstance(data_pandas, Dict)
    assert len(data_pandas) == 2
    assert all(len(data_pandas[sheet_name]) == 6 for sheet_name in sheet_names)
    assert list(data_pandas.keys()) == sheet_names
    for sheet_name in sheet_names:
        assert isinstance(data_pandas[sheet_name], pd.DataFrame)
        assert data_pandas[sheet_name].equals(pd.read_excel(path, header=None, sheet_name=sheet_name))

    excel_data_node_as_pandas_no_sheet_name = ExcelDataNode(
        "bar", Scope.SCENARIO, properties={"path": path, "has_header": False}
    )
    data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
    assert isinstance(data_pandas_no_sheet_name, Dict)
    for key in data_pandas_no_sheet_name.keys():
        assert isinstance(data_pandas_no_sheet_name[key], pd.DataFrame)
        assert data_pandas[key].equals(data_pandas_no_sheet_name[key])

    # Create ExcelDataNode with numpy exposed_type
    excel_data_node_as_numpy = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "sheet_name": sheet_names, "exposed_type": "numpy"},
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
            data_pandas[sheet_name], pd.read_excel(path, header=None, sheet_name=sheet_name).to_numpy()
        )

    excel_data_node_as_numpy_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "exposed_type": "numpy"},
    )

    data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
    assert isinstance(data_numpy_no_sheet_name, Dict)
    for key in data_numpy_no_sheet_name.keys():
        assert isinstance(data_numpy_no_sheet_name[key], np.ndarray)
        assert np.array_equal(data_numpy[key], data_numpy_no_sheet_name[key])

    # Create the same ExcelDataNode but with custom exposed_type
    non_existing_sheet_name_custom = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": path,
            "has_header": False,
            "sheet_name": ["Sheet1", "xyz"],
            "exposed_type": MyCustomObject1,
        },
    )
    with pytest.raises(NonExistingExcelSheet):
        non_existing_sheet_name_custom.read()

    excel_data_node_as_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": path,
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

    excel_data_node_as_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "exposed_type": MyCustomObject1},
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

    with pytest.raises(ExposedTypeLengthMismatch):
        dn = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={
                "path": path,
                "sheet_name": ["Sheet1"],
                "exposed_type": [MyCustomObject1, MyCustomObject2],
                "has_header": False,
            },
        )
        dn.read()

    custom_class_dict = {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

    excel_data_node_as_multi_custom_object = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={
            "path": path,
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
            "path": path,
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

    excel_data_node_as_multi_custom_object_no_sheet_name = ExcelDataNode(
        "bar",
        Scope.SCENARIO,
        properties={"path": path, "has_header": False, "exposed_type": custom_class_dict},
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
