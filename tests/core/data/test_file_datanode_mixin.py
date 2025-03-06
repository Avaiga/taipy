# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import filecmp
import os
import pathlib

from taipy import Scope
from taipy.core.common._utils import _normalize_path
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode


def test_duplicate_data():
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.csv")
    src = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
    copy = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
    copy_2 = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
    copy_copy = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
    _DataManager._set(src)

    src._duplicate_file(copy)
    _DataManager._set(copy)
    assert _normalize_path(src.path) == _normalize_path(path)
    assert _normalize_path(src.path) != _normalize_path(copy.path)
    assert filecmp.cmp(path, copy.path)
    assert src.path.count("DUPLICATE_OF") == 0
    assert copy.path.count("DUPLICATE_OF") == 1

    src._duplicate_file(copy_2)
    _DataManager._set(copy_2)
    assert _normalize_path(copy.path) != _normalize_path(copy_2.path)
    assert copy_2.path.count("DUPLICATE_OF") == 1

    copy._duplicate_file(copy_copy)
    _DataManager._set(copy_copy)
    assert copy_copy.path.count("DUPLICATE_OF") == 2

    os.unlink(copy.path)
    os.unlink(copy_2.path)
    os.unlink(copy_copy.path)
