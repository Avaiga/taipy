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
from unittest.mock import patch

import pytest
from src.taipy.config.config import Config
from src.taipy.core import Core
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.data.excel import ExcelDataNode
from src.taipy.core.data.json import JSONDataNode
from src.taipy.core.data.parquet import ParquetDataNode
from src.taipy.core.data.pickle import PickleDataNode


def read_backup_file(path):
    with open(path, "r") as f:
        lines = f.readlines()
    return lines


@pytest.fixture(scope="function", autouse=True)
def init_backup_file():
    os.environ["TAIPY_BACKUP_FILE_PATH"] = ".taipy_backups"
    if os.path.exists(os.environ["TAIPY_BACKUP_FILE_PATH"]):
        os.remove(os.environ["TAIPY_BACKUP_FILE_PATH"])

    yield

    if os.path.exists(".taipy_backups"):
        os.remove(".taipy_backups")
    del os.environ["TAIPY_BACKUP_FILE_PATH"]


backup_file_path = ".taipy_backups"


def test_backup_storage_folder_when_core_run():
    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run()
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{Config.core.storage_folder}\n"]
    core.stop()


def test_no_new_entry_when_file_is_in_storage_folder():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", path="dn_1.pickle")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2")  # stored in .data folder

    dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)

    dn_1.write("DN1_CONTENT")
    dn_2.write("DN2_CONTENT")

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{dn_1.path}\n"]
    os.remove(dn_1.path)


def test_backup_csv_files():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "csv", path="example_1.csv")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "csv", path="example_2.csv")

    csv_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(csv_dn_1, CSVDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_1.path}\n"]

    csv_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)
    assert isinstance(csv_dn_2, CSVDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_1.path}\n", f"{csv_dn_2.path}\n"]

    csv_dn_1.path = "example_3.csv"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_2.path}\n", f"{csv_dn_1.path}\n"]

    csv_dn_2.path = "example_4.csv"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_1.path}\n", f"{csv_dn_2.path}\n"]

    _DataManager._delete(csv_dn_1.id)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_2.path}\n"]

    csv_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    csv_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(csv_dn_3, CSVDataNode)
    assert isinstance(csv_dn_4, CSVDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_2.path}\n", f"{csv_dn_3.path}\n", f"{csv_dn_4.path}\n"]

    csv_dn_4.path = "example_5.csv"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{csv_dn_2.path}\n", f"{csv_dn_3.path}\n", f"{csv_dn_4.path}\n"]

    _DataManager._delete_all()

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == []


def test_backup_excel_files():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "excel", path="example_1.xlsx")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "excel", path="example_2.xlsx")

    excel_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(excel_dn_1, ExcelDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_1.path}\n"]

    excel_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)
    assert isinstance(excel_dn_2, ExcelDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_1.path}\n", f"{excel_dn_2.path}\n"]

    excel_dn_1.path = "example_3.excel"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_2.path}\n", f"{excel_dn_1.path}\n"]

    excel_dn_2.path = "example_4.excel"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_1.path}\n", f"{excel_dn_2.path}\n"]

    _DataManager._delete(excel_dn_1.id)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_2.path}\n"]

    excel_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    excel_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(excel_dn_3, ExcelDataNode)
    assert isinstance(excel_dn_4, ExcelDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_2.path}\n", f"{excel_dn_3.path}\n", f"{excel_dn_4.path}\n"]

    excel_dn_4.path = "example_5.excel"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{excel_dn_2.path}\n", f"{excel_dn_3.path}\n", f"{excel_dn_4.path}\n"]

    _DataManager._delete_all()

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == []


def test_backup_pickle_files():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "pickle", path="example_1.p")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "pickle", path="example_2.p")

    pickle_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(pickle_dn_1, PickleDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_1.path}\n"]

    pickle_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)
    assert isinstance(pickle_dn_2, PickleDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_1.path}\n", f"{pickle_dn_2.path}\n"]

    pickle_dn_1.path = "example_3.pickle"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_2.path}\n", f"{pickle_dn_1.path}\n"]

    pickle_dn_2.path = "example_4.pickle"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_1.path}\n", f"{pickle_dn_2.path}\n"]

    _DataManager._delete(pickle_dn_1.id)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_2.path}\n"]

    pickle_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    pickle_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(pickle_dn_3, PickleDataNode)
    assert isinstance(pickle_dn_4, PickleDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_2.path}\n", f"{pickle_dn_3.path}\n", f"{pickle_dn_4.path}\n"]

    pickle_dn_4.path = "example_5.pickle"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{pickle_dn_2.path}\n", f"{pickle_dn_3.path}\n", f"{pickle_dn_4.path}\n"]

    _DataManager._delete_all()

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == []


def test_backup_json_files():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "json", path="example_1.json")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "json", path="example_2.json")

    json_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(json_dn_1, JSONDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_1.path}\n"]

    json_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)
    assert isinstance(json_dn_2, JSONDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_1.path}\n", f"{json_dn_2.path}\n"]

    json_dn_1.path = "example_3.json"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_2.path}\n", f"{json_dn_1.path}\n"]

    json_dn_2.path = "example_4.json"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_1.path}\n", f"{json_dn_2.path}\n"]

    _DataManager._delete(json_dn_1.id)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_2.path}\n"]

    json_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    json_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(json_dn_3, JSONDataNode)
    assert isinstance(json_dn_4, JSONDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_2.path}\n", f"{json_dn_3.path}\n", f"{json_dn_4.path}\n"]

    json_dn_4.path = "example_5.json"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{json_dn_2.path}\n", f"{json_dn_3.path}\n", f"{json_dn_4.path}\n"]

    _DataManager._delete_all()

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == []


def test_backup_parquet_files():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "parquet", path="example_1.parquet")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "parquet", path="example_2.parquet")

    parquet_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(parquet_dn_1, ParquetDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_1.path}\n"]

    parquet_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)
    assert isinstance(parquet_dn_2, ParquetDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_1.path}\n", f"{parquet_dn_2.path}\n"]

    parquet_dn_1.path = "example_3.parquet"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_2.path}\n", f"{parquet_dn_1.path}\n"]

    parquet_dn_2.path = "example_4.parquet"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_1.path}\n", f"{parquet_dn_2.path}\n"]

    _DataManager._delete(parquet_dn_1.id)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_2.path}\n"]

    parquet_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    parquet_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)
    assert isinstance(parquet_dn_3, ParquetDataNode)
    assert isinstance(parquet_dn_4, ParquetDataNode)

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_2.path}\n", f"{parquet_dn_3.path}\n", f"{parquet_dn_4.path}\n"]

    parquet_dn_4.path = "example_5.parquet"
    backup_files = read_backup_file(backup_file_path)
    assert backup_files == [f"{parquet_dn_2.path}\n", f"{parquet_dn_3.path}\n", f"{parquet_dn_4.path}\n"]

    _DataManager._delete_all()

    backup_files = read_backup_file(backup_file_path)
    assert backup_files == []


def test_no_backup_if_no_env_var():
    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "csv", path="example_1.csv")
    _DataManager._create_and_set(dn_cfg_1, None, None)
