# Copyright 2022 Avaiga Private Limited
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

from src.taipy.core.common.alias import DataNodeId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.excel import ExcelDataNode
from src.taipy.core.exceptions.exceptions import (
    MissingRequiredProperty,
    NoData,
    NonExistingExcelSheet,
    NotMatchSheetNameAndCustomObject,
)
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope


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
            Scope.PIPELINE,
            name="super name",
            properties={"path": path, "has_header": False, "sheet_name": sheet_names},
        )
        assert isinstance(dn, ExcelDataNode)
        assert dn.storage_type() == "excel"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.last_edition_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False
        assert dn.sheet_name == sheet_names

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"has_header": True})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"sheet_name": "sheet_name"})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode(
                "foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"has_header": True, "sheet_name": "Sheet1"}
            )

    def test_read_with_header(self):
        not_existing_excel = ExcelDataNode("foo", Scope.PIPELINE, properties={"path": "WRONG.xlsx"})
        with pytest.raises(NoData):
            assert not_existing_excel.read() is None
            not_existing_excel.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
        excel_data_node_as_pandas = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "sheet_name": "Sheet1"}
        )

        data_pandas = excel_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 5
        assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path).to_numpy())

        # Create ExcelDataNode with numpy exposed_type
        excel_data_node_as_numpy = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "exposed_type": "numpy", "sheet_name": "Sheet1"}
        )

        data_numpy = excel_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 5
        assert np.array_equal(data_numpy, pd.read_excel(path).to_numpy())

        # Create the same ExcelDataNode but with custom exposed_type
        non_existing_sheet_name_custom = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "sheet_name": "abc", "exposed_type": MyCustomObject},
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_node_as_custom_object = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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

    def test_read_without_header(self):
        not_existing_excel = ExcelDataNode(
            "foo", Scope.PIPELINE, properties={"path": "WRONG.xlsx", "has_header": False}
        )
        with pytest.raises(NoData):
            assert not_existing_excel.read() is None
            not_existing_excel.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
        excel_data_node_as_pandas = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "sheet_name": "Sheet1"}
        )
        data_pandas = excel_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 6
        assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path, header=None).to_numpy())

        # Create ExcelDataNode with numpy exposed_type
        excel_data_node_as_numpy = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": False, "exposed_type": "numpy", "sheet_name": "Sheet1"},
        )

        data_numpy = excel_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 6
        assert np.array_equal(data_numpy, pd.read_excel(path, header=None).to_numpy())

        # Create the same ExcelDataNode but with custom exposed_type
        non_existing_sheet_name_custom = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": False, "sheet_name": "abc", "exposed_type": MyCustomObject},
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_node_as_custom_object = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, excel_file, default_data_frame, content, columns):
        excel_dn = ExcelDataNode("foo", Scope.PIPELINE, properties={"path": excel_file, "sheet_name": "Sheet1"})
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

    def test_read_multi_sheet_with_header(self):
        not_existing_excel = ExcelDataNode(
            "foo",
            Scope.PIPELINE,
            properties={"path": "WRONG.xlsx", "sheet_name": ["sheet_name_1", "sheet_name_2"]},
        )
        with pytest.raises(NoData):
            assert not_existing_excel.read() is None
            not_existing_excel.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]

        # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
        excel_data_node_as_pandas = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "sheet_name": sheet_names}
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

        excel_data_node_as_pandas_no_sheet_name = ExcelDataNode("bar", Scope.PIPELINE, properties={"path": path})

        data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
        assert isinstance(data_pandas_no_sheet_name, Dict)
        assert len(data_pandas_no_sheet_name) == 2
        assert data_pandas.keys() == data_pandas_no_sheet_name.keys()

        for sheet_name in sheet_names:
            assert data_pandas[sheet_name].equals(data_pandas_no_sheet_name[sheet_name])

        # Create ExcelDataNode with numpy exposed_type
        excel_data_node_as_numpy = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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
            Scope.PIPELINE,
            properties={"path": path, "exposed_type": "numpy"},
        )

        data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
        assert isinstance(data_numpy_no_sheet_name, Dict)
        assert len(data_numpy_no_sheet_name) == 2
        assert data_numpy.keys() == data_numpy_no_sheet_name.keys()

        for sheet_name in sheet_names:
            assert np.array_equal(data_numpy[sheet_name], data_numpy_no_sheet_name[sheet_name])

        # Create the same ExcelDataNode but with custom exposed_type
        non_existing_sheet_name_custom = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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
            Scope.PIPELINE,
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
            Scope.PIPELINE,
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

        with pytest.raises(NotMatchSheetNameAndCustomObject):
            _ = ExcelDataNode(
                "bar",
                Scope.PIPELINE,
                properties={
                    "path": path,
                    "sheet_name": ["Sheet1"],
                    "exposed_type": [MyCustomObject1, MyCustomObject2],
                },
            )

        custom_class_dict = {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

        excel_data_node_as_multi_custom_object = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "sheet_name": sheet_names, "exposed_type": custom_class_dict},
        )
        assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

        excel_data_node_as_multi_custom_object = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "sheet_name": sheet_names, "exposed_type": [MyCustomObject1, MyCustomObject2]},
        )
        assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

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
            Scope.PIPELINE,
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

    def test_read_multi_sheet_without_header(self):
        not_existing_excel = ExcelDataNode(
            "foo",
            Scope.PIPELINE,
            properties={"path": "WRONG.xlsx", "has_header": False, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
        )
        with pytest.raises(NoData):
            assert not_existing_excel.read() is None
            not_existing_excel.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]

        # Create ExcelDataNode without exposed_type (Default is pandas.DataFrame)
        excel_data_node_as_pandas = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "sheet_name": sheet_names}
        )
        data_pandas = excel_data_node_as_pandas.read()
        assert isinstance(data_pandas, Dict)
        assert len(data_pandas) == 2
        assert all(len(data_pandas[sheet_name]) == 6 for sheet_name in sheet_names)
        assert list(data_pandas.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert data_pandas[sheet_name].equals(pd.read_excel(path, header=None, sheet_name=sheet_name))

        excel_data_node_as_pandas_no_sheet_name = ExcelDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False}
        )
        data_pandas_no_sheet_name = excel_data_node_as_pandas_no_sheet_name.read()
        assert isinstance(data_pandas_no_sheet_name, Dict)
        assert len(data_pandas_no_sheet_name) == 2
        assert data_pandas.keys() == data_pandas_no_sheet_name.keys()

        for sheet_name in sheet_names:
            assert data_pandas[sheet_name].equals(data_pandas_no_sheet_name[sheet_name])

        # Create ExcelDataNode with numpy exposed_type
        excel_data_node_as_numpy = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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
            Scope.PIPELINE,
            properties={"path": path, "has_header": False, "exposed_type": "numpy"},
        )

        data_numpy_no_sheet_name = excel_data_node_as_numpy_no_sheet_name.read()
        assert isinstance(data_numpy_no_sheet_name, Dict)
        assert len(data_numpy_no_sheet_name) == 2
        assert data_numpy.keys() == data_numpy_no_sheet_name.keys()

        for sheet_name in sheet_names:
            assert np.array_equal(data_numpy[sheet_name], data_numpy_no_sheet_name[sheet_name])

        # Create the same ExcelDataNode but with custom exposed_type
        non_existing_sheet_name_custom = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": False,
                "sheet_name": sheet_names,
                "exposed_type": MyCustomObject1,
            },
        )

        data_custom = excel_data_node_as_custom_object.read()
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
            Scope.PIPELINE,
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

        with pytest.raises(NotMatchSheetNameAndCustomObject):
            _ = ExcelDataNode(
                "bar",
                Scope.PIPELINE,
                properties={
                    "path": path,
                    "sheet_name": ["Sheet1"],
                    "exposed_type": [MyCustomObject1, MyCustomObject2],
                    "has_header": False,
                },
            )

        custom_class_dict = {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

        excel_data_node_as_multi_custom_object = ExcelDataNode(
            "bar",
            Scope.PIPELINE,
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
            Scope.PIPELINE,
            properties={
                "path": path,
                "sheet_name": sheet_names,
                "exposed_type": [MyCustomObject1, MyCustomObject2],
                "has_header": False,
            },
        )
        assert excel_data_node_as_multi_custom_object.properties["exposed_type"] == custom_class_dict

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
            Scope.PIPELINE,
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
            Scope.PIPELINE,
            properties={"path": excel_file_with_multi_sheet, "sheet_name": sheet_names},
        )

        for sheet_name in sheet_names:
            assert np.array_equal(excel_dn.read()[sheet_name].values, default_multi_sheet_data_frame[sheet_name].values)

        multi_sheet_content = {sheet_name: pd.DataFrame(content) for sheet_name in sheet_names}

        excel_dn.write(multi_sheet_content)
        data_pandas = excel_dn.read()

        for sheet_name in sheet_names:
            assert np.array_equal(data_pandas[sheet_name].values, multi_sheet_content[sheet_name].values)

    def test_set_path(self):
        dn = ExcelDataNode("foo", Scope.PIPELINE, properties={"default_path": "foo.xlsx"})
        assert dn.path == "foo.xlsx"
        dn.path = "bar.xlsx"
        assert dn.path == "bar.xlsx"

    def test_raise_error_when_path_not_exist(self):
        with pytest.raises(MissingRequiredProperty):
            ExcelDataNode("foo", Scope.PIPELINE)
