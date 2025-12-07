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

import os
import pathlib
import tempfile

import pytest

from taipy.gui import Gui
from taipy.gui.utils import _get_non_existent_file_path, _secure_filename_unicode


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


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ("normal_file.txt", "normal_file.txt"),
        ("file with spaces.txt", "file_with_spaces.txt"),
        ("file.with.dots.txt", "file.with.dots.txt"),
    ],
)
def test_secure_filename_unicode_valid_cases(gui: Gui, helpers, input_filename, expected_output):
    """Test that valid filenames pass through unchanged"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ('file<>:"/\\|?*.txt', "file_.txt"),
        ("file<s>.txt", "files.txt"),
        ("file:name.txt", "filename.txt"),
        ('file"name".txt', "filename.txt"),
        ("file|name.txt", "filename.txt"),
        ("file\x00\x1f\x7f.txt", "file.txt"),
    ],
)
def test_secure_filename_unicode_special_chars(gui: Gui, helpers, input_filename, expected_output):
    """Test removal of forbidden and control characters"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ("café.txt", "café.txt"),
        ("naïve.txt", "naïve.txt"),
        ("résumé.txt", "résumé.txt"),
        ("测试文件.txt", "测试文件.txt"),
        ("файл.txt", "файл.txt"),
        ("café", "café"),
        ("poup\u00e9e", "poupée"),
        ("cafe\u0301", "café"),
    ],
)
def test_secure_filename_unicode_preservation(gui: Gui, helpers, input_filename, expected_output):
    """Test Unicode character preservation and normalization"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ("  file  .txt  ", "file_.txt"),
        ("file   with   spaces.txt", "file_with_spaces.txt"),
        ("file\nwith\ttabs.txt", "filewithtabs.txt"),
        ("..file.txt", "file.txt"),
        ("file..txt", "file..txt"),
        ("__file__.txt", "file_.txt"),
        (".file_.txt", "file_.txt"),
    ],
)
def test_secure_filename_unicode_whitespace_cleanup(gui: Gui, helpers, input_filename, expected_output):
    """Test whitespace handling and leading/trailing character cleanup"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ("", ""),
        ("   ", ""),
        ("...", ""),
        ("___", ""),
        ('<>:"/\\|?*', ""),
    ],
)
def test_secure_filename_unicode_empty_cases(gui: Gui, helpers, input_filename, expected_output):
    """Test edge cases that result in empty filenames"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output",
    [
        ("My Document (Final Version).pdf", "My_Document_(Final_Version).pdf"),
        ("Report 2024: Q1 Results.xlsx", "Report_2024_Q1_Results.xlsx"),
        ('User\'s File: "Important".docx', "User's_File_Important.docx"),
        ("café & naïve résumé.pdf", "café_&_naïve_résumé.pdf"),
    ],
)
def test_secure_filename_unicode_real_world_cases(gui: Gui, helpers, input_filename, expected_output):
    """Test realistic filename scenarios with mixed issues"""
    assert _secure_filename_unicode(input_filename) == expected_output


@pytest.mark.parametrize(
    "input_filename,expected_output_windows,expected_output_non_windows",
    [
        ("CON.txt", "_CON.txt", "CON.txt"),
        ("PRN.txt", "_PRN.txt", "PRN.txt"),
        ("AUX.txt", "_AUX.txt", "AUX.txt"),
        ("NUL.txt", "_NUL.txt", "NUL.txt"),
        ("COM1.txt", "_COM1.txt", "COM1.txt"),
        ("LPT1.txt", "_LPT1.txt", "LPT1.txt"),
        ("con.txt", "_con.txt", "con.txt"),
        ("Con.Txt", "_Con.Txt", "Con.Txt"),
    ],
)
def test_secure_filename_unicode_windows_device_files(
    gui: Gui, helpers, input_filename, expected_output_windows, expected_output_non_windows
):
    """Test Windows device file handling (platform-specific)"""

    if os.name == "nt":
        assert _secure_filename_unicode(input_filename) == expected_output_windows
    else:
        assert _secure_filename_unicode(input_filename) == expected_output_non_windows
