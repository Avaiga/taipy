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
from time import sleep
from typing import Dict

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
import pytest
from modin.pandas.test.utils import df_equals
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.excel import ExcelDataNode
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.exceptions.exceptions import (
    ExposedTypeLengthMismatch,
    InvalidExposedType,
    NoData,
    NonExistingExcelSheet,
    SheetNameLengthMismatch,
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


class TestExcelDataNode:
    def test_new_excel_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "excel", path="NOT_EXISTING.csv")
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "excel", path=path)

        dns = _DataManager._bulk_get_or_create([not_ready_dn_cfg, ready_dn_cfg])

        assert not dns[not_ready_dn_cfg].is_ready_for_reading
        assert dns[ready_dn_cfg].is_ready_for_reading

    def test_create(self):
        path = "data/node/path"
        sheet_names = ["sheet_name_1", "sheet_name_2"]
        dn = ExcelDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties={"path": path, "has_header": False, "sheet_name": sheet_names, "name": "super name"},
        )
        assert isinstance(dn, ExcelDataNode)
        assert dn.storage_type() == "excel"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.parent_ids == set()
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False
        assert dn.sheet_name == sheet_names

    def test_get_user_properties(self, excel_file):
        dn_1 = ExcelDataNode("dn_1", Scope.SCENARIO, properties={"path": "data/node/path"})
        assert dn_1._get_user_properties() == {}

        dn_2 = ExcelDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "exposed_type": "numpy",
                "default_data": "foo",
                "default_path": excel_file,
                "has_header": False,
                "sheet_name": ["sheet_name_1", "sheet_name_2"],
                "foo": "bar",
            },
        )

        # exposed_type, default_data, default_path, path, has_header are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_read_with_header(self):
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
        excel_data_node_as_pandas = ExcelDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "sheet_name": "Sheet1"}
        )

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

    @pytest.mark.modin
    def test_read_with_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataNode with modin exposed_type
        excel_data_node_as_modin = ExcelDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "sheet_name": "Sheet1", "exposed_type": "modin"}
        )

        data_modin = excel_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 5
        assert np.array_equal(data_modin.to_numpy(), pd.read_excel(path).to_numpy())

    def test_read_without_header(self):
        not_existing_excel = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": "WRONG.xlsx", "has_header": False}
        )
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

    @pytest.mark.modin
    def test_read_without_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        # Create ExcelDataNode with modin exposed_type
        excel_data_node_as_modin = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={"path": path, "has_header": False, "sheet_name": "Sheet1", "exposed_type": "modin"},
        )
        data_modin = excel_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 6
        assert np.array_equal(data_modin.to_numpy(), pd.read_excel(path, header=None).to_numpy())

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, excel_file, default_data_frame, content, columns):
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
    def test_write_with_sheet_name(self, excel_file_with_sheet_name, default_data_frame, content, sheet_name):
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
        self, excel_file_with_sheet_name, default_data_frame, content, sheet_name
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
    def test_write_without_sheet_name(self, excel_file_with_sheet_name, default_data_frame, content):
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
    def test_write_with_column_and_sheet_name(
        self, excel_file_with_sheet_name, default_data_frame, content, columns, sheet_name
    ):
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

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write_modin(self, excel_file, default_data_frame, content, columns):
        excel_dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "modin"}
        )
        assert np.array_equal(excel_dn.read().values, default_data_frame.values)
        if not columns:
            excel_dn.write(content)
            df = modin_pd.DataFrame(content)
        else:
            excel_dn.write_with_column_names(content, columns)
            df = modin_pd.DataFrame(content, columns=columns)

        assert np.array_equal(excel_dn.read().values, df.values)

        excel_dn.write(None)
        assert len(excel_dn.read()) == 0

    def test_read_multi_sheet_with_header(self):
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

    @pytest.mark.modin
    def test_read_multi_sheet_with_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]

        # Create ExcelDataNode with modin exposed_type
        excel_data_node_as_modin = ExcelDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "sheet_name": sheet_names, "exposed_type": "modin"}
        )
        data_modin = excel_data_node_as_modin.read()
        assert isinstance(data_modin, Dict)
        assert len(data_modin) == 2
        assert all(
            len(data_modin[sheet_name] == 5) and isinstance(data_modin[sheet_name], modin_pd.DataFrame)
            for sheet_name in sheet_names
        )
        assert list(data_modin.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert data_modin[sheet_name].equals(modin_pd.read_excel(path, sheet_name=sheet_name))

        excel_data_node_as_pandas_no_sheet_name = ExcelDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "exposed_type": "modin"}
        )

        data_modin_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
        assert isinstance(data_modin_no_sheet_name, Dict)
        for key in data_modin_no_sheet_name.keys():
            assert isinstance(data_modin_no_sheet_name[key], modin_pd.DataFrame)
            assert data_modin[key].equals(data_modin_no_sheet_name[key])

    def test_read_multi_sheet_without_header(self):
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

    @pytest.mark.modin
    def test_read_multi_sheet_without_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]
        # Create ExcelDataNode with modin exposed_type
        excel_data_node_as_modin = ExcelDataNode(
            "bar",
            Scope.SCENARIO,
            properties={"path": path, "has_header": False, "sheet_name": sheet_names, "exposed_type": "modin"},
        )
        data_modin = excel_data_node_as_modin.read()
        assert isinstance(data_modin, Dict)
        assert len(data_modin) == 2
        assert all(len(data_modin[sheet_name]) == 6 for sheet_name in sheet_names)
        assert list(data_modin.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert isinstance(data_modin[sheet_name], modin_pd.DataFrame)
            assert data_modin[sheet_name].equals(pd.read_excel(path, header=None, sheet_name=sheet_name))

        excel_data_node_as_modin_no_sheet_name = ExcelDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "exposed_type": "modin"}
        )
        data_modin_no_sheet_name = excel_data_node_as_modin_no_sheet_name.read()
        assert isinstance(data_modin_no_sheet_name, Dict)
        for key in data_modin_no_sheet_name.keys():
            assert isinstance(data_modin_no_sheet_name[key], modin_pd.DataFrame)
            assert data_modin[key].equals(data_modin_no_sheet_name[key])

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write_multi_sheet(self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content, columns):
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

    def test_write_multi_sheet_numpy(self, excel_file_with_multi_sheet):
        sheet_names = ["Sheet1", "Sheet2"]

        excel_dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": excel_file_with_multi_sheet, "sheet_name": sheet_names, "exposed_type": "numpy"},
        )

        sheets_data = [[11, 22, 33], [44, 55, 66]]
        data = {
            sheet_name: pd.DataFrame(sheet_data).to_numpy() for sheet_name, sheet_data in zip(sheet_names, sheets_data)
        }
        excel_dn.write(data)
        read_data = excel_dn.read()
        assert all(np.array_equal(data[sheet_name], read_data[sheet_name]) for sheet_name in sheet_names)

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write_multi_sheet_with_modin(
        self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content, columns
    ):
        sheet_names = ["Sheet1", "Sheet2"]

        excel_dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": excel_file_with_multi_sheet, "sheet_name": sheet_names, "exposed_type": "modin"},
        )

        for sheet_name in sheet_names:
            assert np.array_equal(excel_dn.read()[sheet_name].values, default_multi_sheet_data_frame[sheet_name].values)

        multi_sheet_content = {sheet_name: modin_pd.DataFrame(content) for sheet_name in sheet_names}

        excel_dn.write(multi_sheet_content)

        for sheet_name in sheet_names:
            assert np.array_equal(excel_dn.read()[sheet_name].values, multi_sheet_content[sheet_name].values)

    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
            ([[11, 22, 33], [44, 55, 66]]),
        ],
    )
    def test_append_pandas_with_sheetname(self, excel_file, default_data_frame, content):
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
    def test_append_pandas_without_sheetname(self, excel_file, default_data_frame, content):
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
    def test_append_pandas_multisheet(self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content):
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
        self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content
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

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (modin_pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
            ([[11, 22, 33], [44, 55, 66]]),
        ],
    )
    def test_append_modin_with_sheetname(self, excel_file, default_data_frame, content):
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "modin"}
        )
        df_equals(dn.read(), modin_pd.DataFrame(default_data_frame))

        dn.append(content)
        df_equals(
            dn.read(),
            modin_pd.concat(
                [modin_pd.DataFrame(default_data_frame), modin_pd.DataFrame(content, columns=["a", "b", "c"])]
            ).reset_index(drop=True),
        )

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (modin_pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
            ([[11, 22, 33], [44, 55, 66]]),
        ],
    )
    def test_append_modin_without_sheetname(self, excel_file, default_data_frame, content):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "modin"})
        df_equals(dn.read()["Sheet1"], default_data_frame)

        dn.append(content)
        df_equals(
            dn.read()["Sheet1"],
            modin_pd.concat([default_data_frame, modin_pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(
                drop=True
            ),
        )

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content",
        [
            (
                {
                    "Sheet1": modin_pd.DataFrame([{"a": 11, "b": 22, "c": 33}]),
                    "Sheet2": modin_pd.DataFrame([{"a": 44, "b": 55, "c": 66}]),
                }
            ),
            (
                {
                    "Sheet1": modin_pd.DataFrame({"a": [11, 44], "b": [22, 55], "c": [33, 66]}),
                    "Sheet2": modin_pd.DataFrame([{"a": 77, "b": 88, "c": 99}]),
                }
            ),
            ({"Sheet1": np.array([[11, 22, 33], [44, 55, 66]]), "Sheet2": np.array([[77, 88, 99]])}),
        ],
    )
    def test_append_modin_multisheet(self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content):
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "path": excel_file_with_multi_sheet,
                "sheet_name": ["Sheet1", "Sheet2"],
                "exposed_type": "modin",
            },
        )
        df_equals(dn.read()["Sheet1"], default_multi_sheet_data_frame["Sheet1"])
        df_equals(dn.read()["Sheet2"], default_multi_sheet_data_frame["Sheet2"])

        dn.append(content)

        df_equals(
            dn.read()["Sheet1"],
            modin_pd.concat(
                [
                    default_multi_sheet_data_frame["Sheet1"],
                    modin_pd.DataFrame(content["Sheet1"], columns=["a", "b", "c"]),
                ]
            ).reset_index(drop=True),
        )
        df_equals(
            dn.read()["Sheet2"],
            modin_pd.concat(
                [
                    default_multi_sheet_data_frame["Sheet2"],
                    modin_pd.DataFrame(content["Sheet2"], columns=["a", "b", "c"]),
                ]
            ).reset_index(drop=True),
        )

    def test_filter_pandas_exposed_type_with_sheetname(self, excel_file):
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "pandas"}
        )
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

    def test_filter_pandas_exposed_type_without_sheetname(self, excel_file):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "pandas"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        assert len(dn.filter(("foo", 1, Operator.EQUAL))["Sheet1"]) == 3
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["Sheet1"]) == 2
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["Sheet1"]) == 3
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["Sheet1"]) == 4

        assert dn["Sheet1"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
        assert dn["Sheet1"]["bar"].equals(pd.Series([1, 2, None, 2, 2]))
        assert dn["Sheet1"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

    def test_filter_pandas_exposed_type_multisheet(self, excel_file):
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": excel_file, "sheet_name": ["sheet_1", "sheet_2"], "exposed_type": "pandas"},
        )
        dn.write(
            {
                "sheet_1": pd.DataFrame(
                    [
                        {"foo": 1, "bar": 1},
                        {"foo": 1, "bar": 2},
                        {"foo": 1},
                        {"foo": 2, "bar": 2},
                        {"bar": 2},
                    ]
                ),
                "sheet_2": pd.DataFrame(
                    [
                        {"foo": 1, "bar": 3},
                        {"foo": 1, "bar": 4},
                        {"foo": 1},
                        {"foo": 2, "bar": 4},
                        {"bar": 4},
                    ]
                ),
            }
        )

        assert len(dn.filter(("foo", 1, Operator.EQUAL))) == 2
        assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_1"]) == 3
        assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_2"]) == 3

        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))) == 2
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_1"]) == 2
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_2"]) == 2

        assert len(dn.filter(("bar", 2, Operator.EQUAL))) == 2
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_1"]) == 3
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_2"]) == 0

        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)) == 2
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_1"]) == 4
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_2"]) == 0

        assert dn["sheet_1"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
        assert dn["sheet_2"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
        assert dn["sheet_1"]["bar"].equals(pd.Series([1, 2, None, 2, 2]))
        assert dn["sheet_2"]["bar"].equals(pd.Series([3, 4, None, 4, 4]))
        assert dn["sheet_1"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))
        assert dn["sheet_2"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 3.0}, {"foo": 1.0, "bar": 4.0}]))

    @pytest.mark.modin
    def test_filter_modin_exposed_type_with_sheetname(self, excel_file):
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "modin"}
        )
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

    @pytest.mark.modin
    def test_filter_modin_exposed_type_without_sheetname(self, excel_file):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "modin"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        assert len(dn.filter(("foo", 1, Operator.EQUAL))["Sheet1"]) == 3
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["Sheet1"]) == 2
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["Sheet1"]) == 3
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["Sheet1"]) == 4

        assert dn["Sheet1"]["foo"].equals(modin_pd.Series([1, 1, 1, 2, None]))
        assert dn["Sheet1"]["bar"].equals(modin_pd.Series([1, 2, None, 2, 2]))
        assert dn["Sheet1"][:2].equals(modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

    @pytest.mark.modin
    def test_filter_modin_exposed_type_multisheet(self, excel_file):
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": excel_file, "sheet_name": ["sheet_1", "sheet_2"], "exposed_type": "modin"},
        )
        dn.write(
            {
                "sheet_1": pd.DataFrame(
                    [
                        {"foo": 1, "bar": 1},
                        {"foo": 1, "bar": 2},
                        {"foo": 1},
                        {"foo": 2, "bar": 2},
                        {"bar": 2},
                    ]
                ),
                "sheet_2": pd.DataFrame(
                    [
                        {"foo": 1, "bar": 3},
                        {"foo": 1, "bar": 4},
                        {"foo": 1},
                        {"foo": 2, "bar": 4},
                        {"bar": 4},
                    ]
                ),
            }
        )

        assert len(dn.filter(("foo", 1, Operator.EQUAL))) == 2
        assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_1"]) == 3
        assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_2"]) == 3

        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))) == 2
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_1"]) == 2
        assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_2"]) == 2

        assert len(dn.filter(("bar", 2, Operator.EQUAL))) == 2
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_1"]) == 3
        assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_2"]) == 0

        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)) == 2
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_1"]) == 4
        assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_2"]) == 0

        assert dn["sheet_1"]["foo"].equals(modin_pd.Series([1, 1, 1, 2, None]))
        assert dn["sheet_2"]["foo"].equals(modin_pd.Series([1, 1, 1, 2, None]))
        assert dn["sheet_1"]["bar"].equals(modin_pd.Series([1, 2, None, 2, 2]))
        assert dn["sheet_2"]["bar"].equals(modin_pd.Series([3, 4, None, 4, 4]))
        assert dn["sheet_1"][:2].equals(modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))
        assert dn["sheet_2"][:2].equals(modin_pd.DataFrame([{"foo": 1.0, "bar": 3.0}, {"foo": 1.0, "bar": 4.0}]))

    def test_filter_numpy_exposed_type_with_sheetname(self, excel_file):
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "numpy"}
        )
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

    def test_filter_numpy_exposed_type_without_sheetname(self, excel_file):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "numpy"})
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

        assert len(dn.filter((0, 1, Operator.EQUAL))["Sheet1"]) == 3
        assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["Sheet1"]) == 3
        assert len(dn.filter((1, 2, Operator.EQUAL))["Sheet1"]) == 2
        assert len(dn.filter([(0, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["Sheet1"]) == 4

        assert np.array_equal(dn["Sheet1"][0], np.array([1, 1]))
        assert np.array_equal(dn["Sheet1"][1], np.array([1, 2]))
        assert np.array_equal(dn["Sheet1"][:3], np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn["Sheet1"][:, 0], np.array([1, 1, 1, 2, 2, 2]))
        assert np.array_equal(dn["Sheet1"][1:4, :1], np.array([[1], [1], [2]]))

    def test_filter_numpy_exposed_type_multisheet(self, excel_file):
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"path": excel_file, "sheet_name": ["sheet_1", "sheet_2"], "exposed_type": "numpy"},
        )
        dn.write(
            {
                "sheet_1": pd.DataFrame(
                    [
                        [1, 1],
                        [1, 2],
                        [1, 3],
                        [2, 1],
                        [2, 2],
                        [2, 3],
                    ]
                ),
                "sheet_2": pd.DataFrame(
                    [
                        [1, 4],
                        [1, 5],
                        [1, 6],
                        [2, 4],
                        [2, 5],
                        [2, 6],
                    ]
                ),
            }
        )

        assert len(dn.filter((0, 1, Operator.EQUAL))) == 2
        assert len(dn.filter((0, 1, Operator.EQUAL))["sheet_1"]) == 3
        assert len(dn.filter((0, 1, Operator.EQUAL))["sheet_2"]) == 3

        assert len(dn.filter((0, 1, Operator.NOT_EQUAL))) == 2
        assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["sheet_1"]) == 3
        assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["sheet_2"]) == 3

        assert len(dn.filter((1, 2, Operator.EQUAL))) == 2
        assert len(dn.filter((1, 2, Operator.EQUAL))["sheet_1"]) == 2
        assert len(dn.filter((1, 2, Operator.EQUAL))["sheet_2"]) == 0

        assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)) == 2
        assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["sheet_1"]) == 4
        assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["sheet_2"]) == 0

        assert np.array_equal(dn["sheet_1"][0], np.array([1, 1]))
        assert np.array_equal(dn["sheet_2"][0], np.array([1, 4]))
        assert np.array_equal(dn["sheet_1"][1], np.array([1, 2]))
        assert np.array_equal(dn["sheet_2"][1], np.array([1, 5]))
        assert np.array_equal(dn["sheet_1"][:3], np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn["sheet_2"][:3], np.array([[1, 4], [1, 5], [1, 6]]))
        assert np.array_equal(dn["sheet_1"][:, 0], np.array([1, 1, 1, 2, 2, 2]))
        assert np.array_equal(dn["sheet_2"][:, 1], np.array([4, 5, 6, 4, 5, 6]))
        assert np.array_equal(dn["sheet_1"][1:4, :1], np.array([[1], [1], [2]]))
        assert np.array_equal(dn["sheet_2"][1:4, 1:2], np.array([[5], [6], [4]]))

    def test_set_path(self):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.xlsx"})
        assert dn.path == "foo.xlsx"
        dn.path = "bar.xlsx"
        assert dn.path == "bar.xlsx"

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({}, False),
            ({"default_data": {"a": ["foo", "bar"]}}, True),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = ExcelDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)
        assert os.path.exists(dn.path) is exists

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write(read_data)
        for sheet, df in dn.read().items():
            assert np.array_equal(df.values, read_data[sheet].values)

    def test_exposed_type_custom_class_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")  # ["Sheet1", "Sheet2"]
        new_path = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example_2.xlsx"
        )  # ["Sheet1", "Sheet2", "Sheet3"]
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": path, "exposed_type": MyCustomObject1})
        assert dn.exposed_type == MyCustomObject1
        dn.read()
        dn.path = new_path
        dn.read()

        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": path, "exposed_type": MyCustomObject1, "sheet_name": ["Sheet4"]},
        )
        assert dn.exposed_type == MyCustomObject1
        with pytest.raises(NonExistingExcelSheet):
            dn.read()

    def test_exposed_type_dict(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")  # ["Sheet1", "Sheet2"]
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_path": path,
                "exposed_type": {
                    "Sheet1": MyCustomObject1,
                    "Sheet2": MyCustomObject2,
                    "Sheet3": MyCustomObject1,
                },
            },
        )
        data = dn.read()
        assert isinstance(data, Dict)
        assert isinstance(data["Sheet1"][0], MyCustomObject1)
        assert isinstance(data["Sheet2"][0], MyCustomObject2)

    def test_exposed_type_list(self):
        path_1 = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx"
        )  # ["Sheet1", "Sheet2"]
        path_2 = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example_2.xlsx"
        )  # ["Sheet1", "Sheet2", "Sheet3"]

        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": path_1, "exposed_type": [MyCustomObject1, MyCustomObject2]},
        )
        data = dn.read()
        assert isinstance(data, Dict)
        assert isinstance(data["Sheet1"][0], MyCustomObject1)
        assert isinstance(data["Sheet2"][0], MyCustomObject2)

        dn.path = path_2
        with pytest.raises(ExposedTypeLengthMismatch):
            dn.read()

    def test_not_trying_to_read_sheet_names_when_exposed_type_is_set(self):
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"default_path": "notexistyet.xlsx", "exposed_type": MyCustomObject1}
        )
        assert dn.path == "notexistyet.xlsx"
        assert dn.exposed_type == MyCustomObject1
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": "notexistyet.xlsx", "exposed_type": [MyCustomObject1, MyCustomObject2]},
        )
        assert dn.path == "notexistyet.xlsx"
        assert dn.exposed_type == [MyCustomObject1, MyCustomObject2]
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_path": "notexistyet.xlsx",
                "exposed_type": {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2},
            },
        )
        assert dn.path == "notexistyet.xlsx"
        assert dn.exposed_type == {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

    def test_exposed_type_default(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": path, "sheet_name": "Sheet1"})
        assert dn.exposed_type == "pandas"
        data = dn.read()
        assert isinstance(data, pd.DataFrame)

    def test_pandas_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"default_path": path, "exposed_type": "pandas", "sheet_name": "Sheet1"}
        )
        assert dn.exposed_type == "pandas"
        data = dn.read()
        assert isinstance(data, pd.DataFrame)

    def test_complex_exposed_type_dict(self):
        # ["Sheet1", "Sheet2", "Sheet3", "Sheet4", "Sheet5"]
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example_4.xlsx")
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_path": path,
                "exposed_type": {
                    "Sheet1": MyCustomObject1,
                    "Sheet2": "numpy",
                    "Sheet3": "pandas",
                },
                "sheet_name": ["Sheet1", "Sheet2", "Sheet3", "Sheet4"],
            },
        )
        data = dn.read()
        assert isinstance(data, dict)
        assert isinstance(data["Sheet1"], list)
        assert isinstance(data["Sheet1"][0], MyCustomObject1)
        assert isinstance(data["Sheet2"], np.ndarray)
        assert isinstance(data["Sheet3"], pd.DataFrame)
        assert isinstance(data["Sheet4"], pd.DataFrame)
        assert data.get("Sheet5") is None

    def test_complex_exposed_type_list(self):
        # ["Sheet1", "Sheet2", "Sheet3", "Sheet4","Sheet5"]
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example_4.xlsx")
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_path": path,
                "exposed_type": [MyCustomObject1, "numpy", "pandas"],
                "sheet_name": ["Sheet1", "Sheet2", "Sheet3"],
            },
        )
        data = dn.read()
        assert isinstance(data, dict)
        assert isinstance(data["Sheet1"], list)
        assert isinstance(data["Sheet1"][0], MyCustomObject1)
        assert isinstance(data["Sheet2"], np.ndarray)
        assert isinstance(data["Sheet3"], pd.DataFrame)

    def test_invalid_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        with pytest.raises(InvalidExposedType):
            ExcelDataNode(
                "foo",
                Scope.SCENARIO,
                properties={"default_path": path, "exposed_type": "invalid", "sheet_name": "Sheet1"},
            )

        with pytest.raises(InvalidExposedType):
            ExcelDataNode(
                "foo",
                Scope.SCENARIO,
                properties={
                    "default_path": path,
                    "exposed_type": ["numpy", "invalid", "pandas"],
                    "sheet_name": "Sheet1",
                },
            )

        with pytest.raises(InvalidExposedType):
            ExcelDataNode(
                "foo",
                Scope.SCENARIO,
                properties={
                    "default_path": path,
                    "exposed_type": {"Sheet1": "pandas", "Sheet2": "invalid"},
                    "sheet_name": "Sheet1",
                },
            )

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.xlsx"))
        pd.DataFrame([]).to_excel(temp_file_path)
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})

        dn.write(pd.DataFrame([1, 2, 3]))
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame([4, 5, 6]).to_excel(temp_file_path)
        new_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write(pd.DataFrame([7, 8, 9]))
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)
