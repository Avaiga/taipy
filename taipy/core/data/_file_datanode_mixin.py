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
import shutil
from datetime import datetime
from os.path import isfile
from typing import Any, Callable, Dict, Optional

from taipy.config.config import Config

from .._entity._reload import _self_reload
from .data_node import DataNode
from .data_node_id import Edit


class _FileDataNodeMixin(object):
    """Mixin class designed to handle file-based data nodes
    (CSVDataNode, ParquetDataNode, ExcelDataNode, PickleDataNode, JSONDataNode, etc.)."""

    __EXTENSION_MAP = {"csv": "csv", "excel": "xlsx", "parquet": "parquet", "pickle": "p", "json": "json"}

    _DEFAULT_DATA_KEY = "default_data"
    _PATH_KEY = "path"
    _DEFAULT_PATH_KEY = "default_path"
    _IS_GENERATED_KEY = "is_generated"

    def __init__(self, properties: Dict) -> None:
        self._path: str = properties.get(self._PATH_KEY, properties.get(self._DEFAULT_PATH_KEY))
        self._is_generated: bool = properties.get(self._IS_GENERATED_KEY, self._path is None)
        self._last_edit_date: Optional[datetime] = None

        if self._path and ".data" in self._path:
            self._path = self._migrate_path(self.storage_type(), self._path)  # type: ignore[attr-defined]
        if not self._path:
            self._path = self._build_path(self.storage_type())  # type: ignore[attr-defined]

        properties[self._IS_GENERATED_KEY] = self._is_generated
        properties[self._PATH_KEY] = self._path

    def _write_default_data(self, default_value: Any):
        if default_value is not None and not os.path.exists(self._path):
            self._write(default_value)  # type: ignore[attr-defined]
            self._last_edit_date = DataNode._get_last_modified_datetime(self._path) or datetime.now()
            self._edits.append(  # type: ignore[attr-defined]
                Edit(
                    {
                        "timestamp": self._last_edit_date,
                        "editor": "TAIPY",
                        "comment": "Default data written.",
                    }
                )
            )

        if not self._last_edit_date and isfile(self._path):
            self._last_edit_date = datetime.now()

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def is_generated(self) -> bool:
        return self._is_generated

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self) -> Any:
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.properties[self._PATH_KEY] = value
        self.properties[self._IS_GENERATED_KEY] = False

    def _build_path(self, storage_type) -> str:
        folder = f"{storage_type}s"
        dir_path = pathlib.Path(Config.core.storage_folder) / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return str(dir_path / f"{self.id}.{self.__EXTENSION_MAP.get(storage_type)}")  # type: ignore[attr-defined]

    def _migrate_path(self, storage_type, old_path) -> str:
        new_path = self._build_path(storage_type)
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
        return new_path

    def _get_downloadable_path(self) -> str:
        """Get the downloadable path of the file data of the data node.

        Returns:
            The downloadable path of the file data of the data node if it exists, otherwise an empty string.
        """
        if os.path.exists(self.path) and isfile(self._path):
            return self.path

        return ""

    def _upload(self, path: str, upload_checker: Optional[Callable[[str, Any], bool]] = None) -> bool:
        """Upload a csv file data to the data node.

        Parameters:
            path (str): The path of the file to upload to the data node.
            upload_checker (Optional[Callable[[str, Any], bool]]): A function to check if the upload is allowed.
                The function takes the title of the upload data and the data itself as arguments and returns
                True if the upload is allowed, otherwise False.

        Returns:
            True if the upload was successful, otherwise False.
        """
        from ._data_manager_factory import _DataManagerFactory

        upload_path = pathlib.Path(path)

        if upload_checker is not None:
            try:
                upload_data = self._read_from_path(upload_path.name)
            except Exception:
                return False

            if not upload_checker(upload_path.name, upload_data):
                return False

        shutil.copy(upload_path, self.path)

        self.track_edit(timestamp=datetime.now())  # type: ignore[attr-defined]
        self.unlock_edit()  # type: ignore[attr-defined]
        _DataManagerFactory._build_manager()._set(self)  # type: ignore[arg-type]

        return True

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        raise NotImplementedError
