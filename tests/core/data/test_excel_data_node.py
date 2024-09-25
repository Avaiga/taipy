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
import uuid
from datetime import datetime, timedelta
from time import sleep
from typing import Dict

import freezegun
import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.common.config.common.scope import Scope
from taipy.common.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.excel import ExcelDataNode
from taipy.core.exceptions.exceptions import (
    ExposedTypeLengthMismatch,
    InvalidExposedType,
    NonExistingExcelSheet,
)
from taipy.core.reason import NoFileToDownload, NotAFile


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
        excel_dn_config = Config.configure_excel_data_node(
            id="foo_bar", default_path=path, has_header=False, sheet_name="Sheet1", name="super name"
        )
        dn = _DataManagerFactory._build_manager()._create_and_set(excel_dn_config, None, None)
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
        assert dn.properties["has_header"] is False
        assert dn.properties["sheet_name"] == "Sheet1"

        excel_dn_config_1 = Config.configure_excel_data_node(
            id="baz", default_path=path, has_header=True, sheet_name="Sheet1", exposed_type=MyCustomObject
        )
        dn_1 = _DataManagerFactory._build_manager()._create_and_set(excel_dn_config_1, None, None)
        assert isinstance(dn_1, ExcelDataNode)
        assert dn_1.properties["has_header"] is True
        assert dn_1.properties["sheet_name"] == "Sheet1"
        assert dn_1.properties["exposed_type"] == MyCustomObject

        excel_dn_config_2 = Config.configure_excel_data_node(
            id="baz",
            default_path=path,
            has_header=True,
            sheet_name=sheet_names,
            exposed_type={"Sheet1": "pandas", "Sheet2": "numpy"},
        )
        dn_2 = _DataManagerFactory._build_manager()._create_and_set(excel_dn_config_2, None, None)
        assert isinstance(dn_2, ExcelDataNode)
        assert dn_2.properties["sheet_name"] == sheet_names
        assert dn_2.properties["exposed_type"] == {"Sheet1": "pandas", "Sheet2": "numpy"}

        excel_dn_config_3 = Config.configure_excel_data_node(
            id="baz", default_path=path, has_header=True, sheet_name=sheet_names, exposed_type=MyCustomObject
        )
        dn_3 = _DataManagerFactory._build_manager()._create_and_set(excel_dn_config_3, None, None)
        assert isinstance(dn_3, ExcelDataNode)
        assert dn_3.properties["sheet_name"] == sheet_names
        assert dn_3.properties["exposed_type"] == MyCustomObject

        excel_dn_config_4 = Config.configure_excel_data_node(
            id="baz",
            default_path=path,
            has_header=True,
            sheet_name=sheet_names,
            exposed_type={"Sheet1": MyCustomObject, "Sheet2": MyCustomObject2},
        )
        dn_4 = _DataManagerFactory._build_manager()._create_and_set(excel_dn_config_4, None, None)
        assert isinstance(dn_4, ExcelDataNode)
        assert dn_4.properties["sheet_name"] == sheet_names
        assert dn_4.properties["exposed_type"] == {"Sheet1": MyCustomObject, "Sheet2": MyCustomObject2}

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

    def test_modin_deprecated_in_favor_of_pandas(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        # Create ExcelDataNode with modin exposed_type
        props = {"path": path, "sheet_name": "Sheet1", "exposed_type": "modin"}
        modin_dn = ExcelDataNode("bar", Scope.SCENARIO, properties=props)
        assert modin_dn.properties["exposed_type"] == "pandas"
        data_modin = modin_dn.read()
        assert isinstance(data_modin, pd.DataFrame)

    def test_set_path(self):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.xlsx"})
        assert dn.path == "foo.xlsx"
        dn.path = "bar.xlsx"
        assert dn.path == "bar.xlsx"

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({"default_data": {"a": ["foo", "bar"]}}, True),
            ({}, False),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = ExcelDataNode("foo", Scope.SCENARIO, DataNodeId(f"dn_id_{uuid.uuid4()}"), properties=properties)
        assert dn.path == os.path.join(Config.core.storage_folder.strip("/"), "excels", dn.id + ".xlsx")
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
        assert dn.properties["exposed_type"] == MyCustomObject1
        dn.read()
        dn.path = new_path
        dn.read()

        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": path, "exposed_type": MyCustomObject1, "sheet_name": ["Sheet4"]},
        )
        assert dn.properties["exposed_type"] == MyCustomObject1
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
        assert dn.properties["exposed_type"] == MyCustomObject1
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": "notexistyet.xlsx", "exposed_type": [MyCustomObject1, MyCustomObject2]},
        )
        assert dn.path == "notexistyet.xlsx"
        assert dn.properties["exposed_type"] == [MyCustomObject1, MyCustomObject2]
        dn = ExcelDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_path": "notexistyet.xlsx",
                "exposed_type": {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2},
            },
        )
        assert dn.path == "notexistyet.xlsx"
        assert dn.properties["exposed_type"] == {"Sheet1": MyCustomObject1, "Sheet2": MyCustomObject2}

    def test_exposed_type_default(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"default_path": path, "sheet_name": "Sheet1"})
        assert dn.properties["exposed_type"] == "pandas"
        data = dn.read()
        assert isinstance(data, pd.DataFrame)

    def test_pandas_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode(
            "foo", Scope.SCENARIO, properties={"default_path": path, "exposed_type": "pandas", "sheet_name": "Sheet1"}
        )
        assert dn.properties["exposed_type"] == "pandas"
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

    def test_migrate_to_new_path(self, tmp_path):
        _base_path = os.path.join(tmp_path, ".data")
        path = os.path.join(_base_path, "test.xlsx")
        # create a file on old path
        os.mkdir(_base_path)
        with open(path, "w"):
            pass

        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})

        assert ".data" not in dn.path
        assert os.path.exists(dn.path)

    def test_is_downloadable(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        reasons = dn.is_downloadable()
        assert reasons
        assert reasons.reasons == ""

    def test_is_not_downloadable_no_file(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/wrong_path.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        reasons = dn.is_downloadable()
        assert not reasons
        assert len(reasons._reasons) == 1
        assert str(NoFileToDownload(path, dn.id)) in reasons.reasons

    def test_is_not_downloadable_not_a_file(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        reasons = dn.is_downloadable()
        assert not reasons
        assert len(reasons._reasons) == 1
        assert str(NotAFile(path, dn.id)) in reasons.reasons

    def test_get_download_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        assert dn._get_downloadable_path() == path

    def test_get_downloadable_path_with_not_existing_file(self):
        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": "NOT_EXISTING.xlsx", "exposed_type": "pandas"})
        assert dn._get_downloadable_path() == ""

    def test_upload(self, excel_file, tmpdir_factory):
        old_xlsx_path = tmpdir_factory.mktemp("data").join("df.xlsx").strpath
        old_data = pd.DataFrame([{"a": 0, "b": 1, "c": 2}, {"a": 3, "b": 4, "c": 5}])

        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": old_xlsx_path, "exposed_type": "pandas"})
        dn.write(old_data)
        old_last_edit_date = dn.last_edit_date

        upload_content = pd.read_excel(excel_file)

        with freezegun.freeze_time(old_last_edit_date + timedelta(seconds=1)):
            dn._upload(excel_file)

        assert_frame_equal(dn.read()["Sheet1"], upload_content)  # The data of dn should change to the uploaded content
        assert dn.last_edit_date > old_last_edit_date
        assert dn.path == old_xlsx_path  # The path of the dn should not change

    def test_upload_with_upload_check_pandas(self, excel_file, tmpdir_factory):
        old_xlsx_path = tmpdir_factory.mktemp("data").join("df.xlsx").strpath
        old_data = pd.DataFrame([{"a": 0, "b": 1, "c": 2}, {"a": 3, "b": 4, "c": 5}])

        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": old_xlsx_path, "exposed_type": "pandas"})
        dn.write(old_data)
        old_last_edit_date = dn.last_edit_date

        def check_data_column(upload_path, upload_data):
            """Check if the uploaded data has the correct file format and
            the sheet named "Sheet1" has the correct columns.
            """
            return upload_path.endswith(".xlsx") and upload_data["Sheet1"].columns.tolist() == ["a", "b", "c"]

        not_exists_xlsx_path = tmpdir_factory.mktemp("data").join("not_exists.xlsx").strpath
        reasons = dn._upload(not_exists_xlsx_path, upload_checker=check_data_column)
        assert bool(reasons) is False
        assert (
            str(list(reasons._reasons[dn.id])[0]) == "The uploaded file not_exists.xlsx can not be read,"
            f' therefore is not a valid data file for data node "{dn.id}"'
        )

        not_xlsx_path = tmpdir_factory.mktemp("data").join("wrong_format_df.xlsm").strpath
        old_data.to_excel(not_xlsx_path, index=False)
        # The upload should fail when the file is not a xlsx
        reasons = dn._upload(not_xlsx_path, upload_checker=check_data_column)
        assert bool(reasons) is False
        assert (
            str(list(reasons._reasons[dn.id])[0])
            == f'The uploaded file wrong_format_df.xlsm has invalid data for data node "{dn.id}"'
        )

        wrong_format_xlsx_path = tmpdir_factory.mktemp("data").join("wrong_format_df.xlsx").strpath
        pd.DataFrame([{"a": 1, "b": 2, "d": 3}, {"a": 4, "b": 5, "d": 6}]).to_excel(wrong_format_xlsx_path, index=False)
        # The upload should fail when check_data_column() return False
        reasons = dn._upload(wrong_format_xlsx_path, upload_checker=check_data_column)
        assert bool(reasons) is False
        assert (
            str(list(reasons._reasons[dn.id])[0])
            == f'The uploaded file wrong_format_df.xlsx has invalid data for data node "{dn.id}"'
        )

        assert_frame_equal(dn.read()["Sheet1"], old_data)  # The content of the dn should not change when upload fails
        assert dn.last_edit_date == old_last_edit_date  # The last edit date should not change when upload fails
        assert dn.path == old_xlsx_path  # The path of the dn should not change

        # The upload should succeed when check_data_column() return True
        assert dn._upload(excel_file, upload_checker=check_data_column)

    def test_upload_with_upload_check_numpy(self, tmpdir_factory):
        old_excel_path = tmpdir_factory.mktemp("data").join("df.xlsx").strpath
        old_data = np.array([[1, 2, 3], [4, 5, 6]])

        new_excel_path = tmpdir_factory.mktemp("data").join("new_upload_data.xlsx").strpath
        new_data = np.array([[1, 2, 3], [4, 5, 6]])
        pd.DataFrame(new_data).to_excel(new_excel_path, index=False)

        dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": old_excel_path, "exposed_type": "numpy"})
        dn.write(old_data)
        old_last_edit_date = dn.last_edit_date

        def check_data_is_positive(upload_path, upload_data):
            return upload_path.endswith(".xlsx") and np.all(upload_data["Sheet1"] > 0)

        not_exists_xlsx_path = tmpdir_factory.mktemp("data").join("not_exists.xlsx").strpath
        reasons = dn._upload(not_exists_xlsx_path, upload_checker=check_data_is_positive)
        assert bool(reasons) is False
        assert (
            str(list(reasons._reasons[dn.id])[0]) == "The uploaded file not_exists.xlsx can not be read,"
            f' therefore is not a valid data file for data node "{dn.id}"'
        )

        wrong_format_not_excel_path = tmpdir_factory.mktemp("data").join("wrong_format_df.xlsm").strpath
        pd.DataFrame(old_data).to_excel(wrong_format_not_excel_path, index=False)
        # The upload should fail when the file is not a excel
        reasons = dn._upload(wrong_format_not_excel_path, upload_checker=check_data_is_positive)
        assert bool(reasons) is False
        assert (
            str(list(reasons._reasons[dn.id])[0])
            == f'The uploaded file wrong_format_df.xlsm has invalid data for data node "{dn.id}"'
        )

        not_xlsx_path = tmpdir_factory.mktemp("data").join("wrong_format_df.xlsx").strpath
        pd.DataFrame(np.array([[-1, 2, 3], [-4, -5, -6]])).to_excel(not_xlsx_path, index=False)
        # The upload should fail when check_data_is_positive() return False
        reasons = dn._upload(not_xlsx_path, upload_checker=check_data_is_positive)
        assert (
            str(list(reasons._reasons[dn.id])[0])
            == f'The uploaded file wrong_format_df.xlsx has invalid data for data node "{dn.id}"'
        )

        np.array_equal(dn.read()["Sheet1"], old_data)  # The content of the dn should not change when upload fails
        assert dn.last_edit_date == old_last_edit_date  # The last edit date should not change when upload fails
        assert dn.path == old_excel_path  # The path of the dn should not change

        # The upload should succeed when check_data_is_positive() return True
        assert dn._upload(new_excel_path, upload_checker=check_data_is_positive)
