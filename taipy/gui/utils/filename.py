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
import re
import unicodedata
from pathlib import Path

_WINDOWS_DEVICE_FILES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def _get_non_existent_file_path(dir_path: Path, file_name: str) -> Path:
    if not file_name:
        file_name = "taipy_file.bin"
    file_path = dir_path / file_name
    index = 0
    file_stem = file_path.stem
    file_suffix = file_path.suffix
    while file_path.exists():
        file_path = dir_path / f"{file_stem}.{index}{file_suffix}"
        index += 1
    return file_path


def _secure_filename_unicode(filename: str) -> str:
    r"""
    Sanitizes a filename for safe filesystem use while preserving Unicode characters.

    This function removes or replaces characters that are invalid or unsafe for filenames,
    normalizes Unicode characters, replaces path separators with spaces, and ensures
    compatibility with Windows device filenames.

    Parameters:
        filename (str): The original filename to sanitize.

    Returns:
        str: The sanitized filename, safe for use on most filesystems. Returns an empty string
        if the input is invalid or results in an empty filename after sanitization.

    Important:
        - Preserves Unicode characters using NFC normalization.
        - Removes invalid characters (e.g., < > : " / \ | ? * and control characters).
        - Replaces path separators with spaces.
        - Converts whitespace to underscores and collapses multiple underscores.
        - Strips leading/trailing dots and underscores.
        - On Windows, prepends an underscore if the filename matches a reserved device name.
    """
    filename = unicodedata.normalize("NFC", filename)

    for sep in os.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "", filename)

    # Replace all whitespace (including newlines, tabs) with spaces
    filename = re.sub(r"\s+", " ", filename)

    # Convert spaces to underscores and clean up multiple underscores
    filename = re.sub(r"_+", "_", filename.replace(" ", "_"))

    # Remove leading/trailing dots and underscores
    filename = filename.strip("._")

    # Windows device file check
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _WINDOWS_DEVICE_FILES:
        filename = f"_{filename}"

    return filename
