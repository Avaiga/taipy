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

import pathlib
import tempfile

from taipy.gui import Gui
from taipy.gui.utils import _get_non_existent_file_path


def test_empty_file_name(gui: Gui, helpers):
    assert _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").name


def test_non_existent_file(gui: Gui, helpers):
    assert not _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "").exists()


def test_existent_file(gui: Gui, helpers):
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    with open(file_path, "w") as file_handler:
        file_handler.write("hello")
    assert file_path.exists()
    file_stem = file_path.stem.split(".", 1)[0]
    file_suffix = file_path.suffixes[-1]
    index = int(file_path.suffixes[0][1:]) if len(file_path.suffixes) > 1 else -1
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    assert file_path.name == f"{file_stem}.{index + 1}{file_suffix}"
    with open(file_path, "w") as file_handler:
        file_handler.write("hello 2")
    assert file_path.exists()
    file_path = _get_non_existent_file_path(pathlib.Path(tempfile.gettempdir()), "")
    assert file_path.name == f"{file_stem}.{index + 2}{file_suffix}"
