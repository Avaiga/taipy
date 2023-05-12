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
from typing import Optional


class _AbstractFileDataNode(object):
    """Abstract base class for data node implementations (CSVDataNode, ParquetDataNode, ExcelDataNode,
    PickleDataNode and JSONDataNode) that are file based."""

    __EXTENSION_MAP = {"csv": "csv", "excel": "xlsx", "parquet": "parquet", "pickle": "p", "json": "json"}

    def _build_path(self, storage_type):
        from taipy.config.config import Config

        folder = f"{storage_type}s"
        dir_path = pathlib.Path(Config.global_config.storage_folder) / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{self.id}.{self.__EXTENSION_MAP.get(storage_type)}"

    @staticmethod
    def _check_and_update_preserve_file(old_path: Optional[str] = None, new_path: Optional[str] = None):
        if preserve_file_path := os.getenv("TAIPY_PRESERVE_FILE_PATH"):
            if old_path and pathlib.Path(preserve_file_path).is_file():
                with open(preserve_file_path, "r+") as f:
                    lines = f.readlines()
                    old_path = f"{old_path}\n"
                    if old_path in lines:
                        f.seek(0)
                        f.truncate()
                        lines.remove(old_path)
                        f.writelines(lines)
            if new_path:
                with open(preserve_file_path, "a") as f:
                    f.write(f"{new_path}\n")
