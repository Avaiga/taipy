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

__BACKUP_FILE_PATH_ENVIRONMENT_VARIABLE_NAME = "TAIPY_BACKUP_FILE_PATH"


def append_to_backup_file(new_file_path: str):
    if preserve_file_path := os.getenv(__BACKUP_FILE_PATH_ENVIRONMENT_VARIABLE_NAME):
        with open(preserve_file_path, "a") as f:
            f.write(f"{new_file_path}\n")


def remove_from_backup_file(to_remove_file_path: str):
    preserve_file_path = os.getenv(__BACKUP_FILE_PATH_ENVIRONMENT_VARIABLE_NAME, None)
    if preserve_file_path and pathlib.Path(preserve_file_path).is_file():
        with open(preserve_file_path, "r+") as f:
            lines = f.readlines()
            to_remove_file_path = f"{to_remove_file_path}\n"
            if to_remove_file_path in lines:
                f.seek(0)
                f.truncate()
                lines.remove(to_remove_file_path)
                f.writelines(lines)


def replace_in_backup_file(old_file_path: str, new_file_path: str):
    remove_from_backup_file(old_file_path)
    append_to_backup_file(new_file_path)
