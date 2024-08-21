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

import json

from .._repository._filesystem_repository import _FileSystemRepository
from ._version_converter import _VersionConverter
from ._version_model import _VersionModel


class _VersionFSRepository(_FileSystemRepository):
    _LATEST_VERSION_KEY = "latest_version"
    _DEVELOPMENT_VERSION_KEY = "development_version"

    def __init__(self) -> None:
        super().__init__(model_type=_VersionModel, converter=_VersionConverter, dir_name="version")

    @property
    def _version_file_path(self):
        return super()._storage_folder / "version.json"

    def _delete_all(self):
        super()._delete_all()

        if self._version_file_path.exists():
            self._version_file_path.unlink()

    def _set_latest_version(self, version_number):
        if self._version_file_path.exists():
            with open(self._version_file_path, "r") as f:
                file_content = json.load(f)
            file_content[self._LATEST_VERSION_KEY] = version_number
        else:
            self.dir_path.mkdir(parents=True, exist_ok=True)
            file_content = {
                self._LATEST_VERSION_KEY: version_number,
                self._DEVELOPMENT_VERSION_KEY: "",
            }
        self._version_file_path.write_text(
            json.dumps(
                file_content,
                ensure_ascii=False,
                indent=0,
            )
        )

    def _get_latest_version(self) -> str:
        with open(self._version_file_path, "r") as f:
            file_content = json.load(f)
        return file_content[self._LATEST_VERSION_KEY]

    def _set_development_version(self, version_number):
        if self._version_file_path.exists():
            with open(self._version_file_path, "r") as f:
                file_content = json.load(f)

            file_content[self._DEVELOPMENT_VERSION_KEY] = version_number
            file_content[self._LATEST_VERSION_KEY] = version_number
        else:
            self.dir_path.mkdir(parents=True, exist_ok=True)
            file_content = {
                self._LATEST_VERSION_KEY: version_number,
                self._DEVELOPMENT_VERSION_KEY: version_number,
            }
        self._version_file_path.write_text(
            json.dumps(
                file_content,
                ensure_ascii=False,
                indent=0,
            )
        )

    def _get_development_version(self) -> str:
        with open(self._version_file_path, "r") as f:
            file_content = json.load(f)
        return file_content[self._DEVELOPMENT_VERSION_KEY]
