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
    if preserve_file_path:
       try: # The file will mostly be present, so testing if the file exists will cost you more than a simple test.
          with open(preserve_file_path, "r+") as f:
              old_backup = f.read()  # No parsing needs
              to_remove_file_path = to_remove_file_path + "\n"
              # If to_remove_file_path can be several times in the string
              new_backup = old_backup.replace(to_remove_file_path, '')
              # otherwise
              new_backup = old_backup.replace(to_remove_file_path, '', 1)
              if new_backup is not old_backup:
                  f.seek(0)
                  f.write(new_backup)
                  # To verify, but I think it is better in that way.
                  # The idea is to write new content on top of the current content then resize the file.
                  f.truncate()
         except: ....


def replace_in_backup_file(old_file_path: str, new_file_path: str):
    remove_from_backup_file(old_file_path)
    append_to_backup_file(new_file_path)
