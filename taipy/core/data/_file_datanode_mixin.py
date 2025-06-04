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
import shutil
from datetime import datetime
from os.path import isfile
from typing import Any, Callable, Dict, Optional, cast

from taipy.common.config import Config
from taipy.common.logger._taipy_logger import _TaipyLogger

from .._entity._reload import _self_reload
from ..common._utils import _normalize_path
from ..reason import (
    DataNodeEditInProgress,
    InvalidUploadFile,
    NoFileToDownload,
    NotAFile,
    ReasonCollection,
    UploadFileCanNotBeRead,
)
from .data_node import DataNode
from .data_node_id import Edit


class _FileDataNodeMixin:
    """Mixin class designed to handle file-based data nodes."""

    __EXTENSION_MAP = {"csv": "csv", "excel": "xlsx", "parquet": "parquet", "pickle": "p", "json": "json"}

    _DEFAULT_DATA_KEY = "default_data"
    _PATH_KEY = "path"
    _DEFAULT_PATH_KEY = "default_path"
    _IS_GENERATED_KEY = "is_generated"
    __TAIPY_DUPLICATE = "DUPLICATE_OF"

    __logger = _TaipyLogger._get_logger()

    def __init__(self, properties: Dict) -> None:
        self._path: str = cast(str, properties.get(self._PATH_KEY, properties.get(self._DEFAULT_PATH_KEY)))
        self._is_generated: bool = properties.get(self._IS_GENERATED_KEY, self._path is None)
        self._last_edit_date: Optional[datetime] = None

        if self._path and ".data" in self._path:
            self._path = self._migrate_path(self.storage_type(), self._path)  # type: ignore[attr-defined]
        if not self._path:
            self._path = self._build_path(self.storage_type())  # type: ignore[attr-defined]

        properties[self._IS_GENERATED_KEY] = self._is_generated
        properties[self._PATH_KEY] = self._path

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def is_generated(self) -> bool:
        """Indicates if the file is generated."""
        return self._is_generated

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self) -> str:
        """The path to the file data of the data node."""
        return _normalize_path(self._path)

    @path.setter
    def path(self, value) -> None:
        _path = _normalize_path(value)
        self._path = _path
        self.properties[self._PATH_KEY] = _path  # type: ignore[attr-defined]
        self.properties[self._IS_GENERATED_KEY] = False  # type: ignore[attr-defined]

    def is_downloadable(self) -> ReasonCollection:
        """Check if the data node is downloadable.

        Returns:
            A `ReasonCollection^` object containing the reasons why the data node is not downloadable.
        """
        collection = ReasonCollection()
        if not os.path.exists(self.path):
            collection._add_reason(self.id, NoFileToDownload(self.path, self.id))  # type: ignore[attr-defined]
        elif not isfile(self.path):
            collection._add_reason(self.id, NotAFile(self.path, self.id))  # type: ignore[attr-defined]
        return collection

    def is_uploadable(self) -> ReasonCollection:
        """Check if the data node is upload-able.

        Returns:
            A `ReasonCollection^` object containing the reasons why the data node is not upload-able.
        """
        return ReasonCollection()

    def _get_downloadable_path(self) -> str:
        """Get the downloadable path of the file data of the data node.

        Returns:
            The downloadable path of the file data of the data node if it exists, otherwise an empty string.
        """
        if os.path.exists(self.path) and isfile(self._path):
            return self.path

        return ""

    def _upload(
        self,
        path: str,
        upload_checker: Optional[Callable[[str, Any], bool]] = None,
        editor_id: Optional[str] = None,
        comment: Optional[str] = None,
        **kwargs: Any,
    ) -> ReasonCollection:
        """Upload a file data to the data node.

        Arguments:
            path (str): The path of the file to upload to the data node.
            upload_checker (Optional[Callable[[str, Any], bool]]): A function to check if the
                upload is allowed. The function takes the title of the upload data and the data
                itself as arguments and returns True if the upload is allowed, otherwise False.
            editor_id (Optional[str]): The ID of the user who is uploading the file.
            comment (Optional[str]): A comment to add to the edit history of the data node.
            **kwargs: Additional keyword arguments. These arguments are stored in the edit
                history of the data node. In particular, an `editor_id` or a `comment` can be
                passed. The `editor_id` is the ID of the user who is uploading the file, and the
                `comment` is a comment to add to the edit history.

        Returns:
            True if the upload was successful, the reasons why the upload was not successful
            otherwise.
        """
        from ._data_manager_factory import _DataManagerFactory

        reasons = ReasonCollection()
        if (
            editor_id
            and self.edit_in_progress  # type: ignore[attr-defined]
            and self.editor_id != editor_id  # type: ignore[attr-defined]
            and (
                not self.editor_expiration_date  # type: ignore[attr-defined]
                or self.editor_expiration_date > datetime.now()  # type: ignore[attr-defined]
            )
        ):
            reasons._add_reason(self.id, DataNodeEditInProgress(self.id))  # type: ignore[attr-defined]
            return reasons

        up_path = pathlib.Path(path)
        try:
            upload_data = self._read_from_path(str(up_path))
        except Exception as err:
            self.__logger.error(f"Error uploading `{up_path.name}` to data " f"node `{self.id}`:")  # type: ignore[attr-defined]
            self.__logger.error(f"Error: {err}")
            reasons._add_reason(self.id, UploadFileCanNotBeRead(up_path.name, self.id))  # type: ignore[attr-defined]
            return reasons

        if upload_checker is not None:
            try:
                can_upload = upload_checker(up_path.name, upload_data)
            except Exception as err:
                self.__logger.error(
                    f"Error with the upload checker `{upload_checker.__name__}` "
                    f"while checking `{up_path.name}` file for upload to the data "
                    f"node `{self.id}`:"  # type: ignore[attr-defined]
                )
                self.__logger.error(f"Error: {err}")
                can_upload = False

            if not can_upload:
                reasons._add_reason(self.id, InvalidUploadFile(up_path.name, self.id))  # type: ignore[attr-defined]
                return reasons

        shutil.copy(up_path, self.path)

        self.track_edit(  # type: ignore[attr-defined]
            timestamp=datetime.now(),
            editor_id=editor_id,
            comment=comment,
            **kwargs,
        )
        self.unlock_edit()  # type: ignore[attr-defined]

        _DataManagerFactory._build_manager()._update(self)  # type: ignore[arg-type]

        return reasons

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        raise NotImplementedError

    def _write_default_data(self, default_value: Any):
        if default_value is not None and not os.path.exists(self._path):
            self._write(default_value)  # type: ignore[attr-defined]
            self._last_edit_date = self._get_last_modified_datetime() or datetime.now()
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

    def _get_last_modified_datetime(self) -> Optional[datetime]:
        if self._path and os.path.isfile(self._path):
            return datetime.fromtimestamp(os.path.getmtime(self._path))

        last_modified_datetime = None
        if self._path and os.path.isdir(self._path):
            for filename in os.listdir(self._path):
                filepath = os.path.join(self._path, filename)
                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                    if last_modified_datetime is None or file_mtime > last_modified_datetime:
                        last_modified_datetime = file_mtime

        return last_modified_datetime

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

    def _duplicate_file(self, dest: DataNode):
        if os.path.exists(self._path):
            folder_path, base_name = os.path.split(self._path)
            new_path = os.path.join(folder_path, f"{dest.id}_{self.__TAIPY_DUPLICATE}_{base_name}")
            if os.path.isdir(self._path):
                shutil.copytree(self._path, new_path)
            else:
                shutil.copy(self._path, new_path)
            normalize_path = _normalize_path(new_path)
            dest._path = normalize_path # type: ignore[attr-defined]
            dest._properties[self._PATH_KEY] = normalize_path
