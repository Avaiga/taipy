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

from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.csv import CSVDataNode
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def test_update_preserve_file():
    def read_preserve_file(path):
        with open(path, "r") as f:
            lines = f.readlines()
        return lines

    preserve_file_path = "./tests/core/data/data_sample/.taipy_preserves"
    os.environ["TAIPY_PRESERVE_FILE_PATH"] = preserve_file_path

    dn_cfg_1 = Config.configure_data_node("dn_cfg_1", "csv", path="example_1.csv")
    dn_cfg_2 = Config.configure_data_node("dn_cfg_2", "csv", path="example_2.csv")

    csv_dn_1 = _DataManager._create_and_set(dn_cfg_1, None, None)

    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_1.path}\n"]

    csv_dn_2 = _DataManager._create_and_set(dn_cfg_2, None, None)

    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_1.path}\n", f"{csv_dn_2.path}\n"]

    csv_dn_1.path = "example_3.csv"
    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_2.path}\n", f"{csv_dn_1.path}\n"]

    csv_dn_2.path = "example_4.csv"
    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_1.path}\n", f"{csv_dn_2.path}\n"]

    _DataManager._delete(csv_dn_1.id)

    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_2.path}\n"]

    csv_dn_3 = _DataManager._create_and_set(dn_cfg_1, None, None)
    csv_dn_4 = _DataManager._create_and_set(dn_cfg_1, None, None)

    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_2.path}\n", f"{csv_dn_3.path}\n", f"{csv_dn_4.path}\n"]

    csv_dn_4.path = "example_5.csv"
    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == [f"{csv_dn_2.path}\n", f"{csv_dn_3.path}\n", f"{csv_dn_4.path}\n"]

    _DataManager._delete_all()

    preserve_files = read_preserve_file(preserve_file_path)
    assert preserve_files == []

    os.remove(preserve_file_path)
