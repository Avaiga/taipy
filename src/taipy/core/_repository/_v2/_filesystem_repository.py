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

import json
import pathlib
import shutil
from typing import Any, Iterable, Iterator, List, Optional, Type, Union

from src.taipy.core.common.typing import Entity, Json, ModelType
from taipy.config.config import Config

from ...exceptions import InvalidExportPath, ModelNotFound
from ._repository import _AbstractRepository, _CustomDecoder, _CustomEncoder


class _FileSystemRepository(_AbstractRepository[ModelType, Entity]):
    """
    Holds common methods to be used and extended when the need for saving
    dataclasses as JSON files in local storage emerges.

    Some lines have type: ignore because MyPy won't recognize some generic attributes. This
    should be revised in the future.

    Attributes:
        model (ModelType): Generic dataclass.
        dir_name (str): Folder that will hold the files for this dataclass model.
    """

    def __init__(self, model: Type[ModelType], dir_name: str):
        self.model = model
        self._dir_name = dir_name

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)

    def _save(self, entity: Entity):
        self.__create_directory_if_not_exists()

        # TODO: implement __from_entity on models
        model = self.model.__from_entity(entity)
        self.__get_model_filepath(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_CustomEncoder, check_circular=False)
        )

    def _get(self, filepath: pathlib.Path) -> Json:
        with pathlib.Path(filepath).open(encoding="UTF-8") as source:
            return json.load(source)

    def load(self, model_id: str) -> Entity:
        try:
            model = self.model(**self._get(self.__get_model_filepath(model_id)))
            return model.__to_entity()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _load_all(self, version_number: Optional[str]) -> List[Entity]:
        """
        Load all entities from a specific version.
        """
        from ..._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        r = []
        try:
            for f in self.dir_path.iterdir():
                if entity := self.model.__to_entity(
                    f, retry=Config.global_config.read_entity_retry or 0, version_number=version_number
                ):
                    r.append(entity)
        except FileNotFoundError:
            pass
        return r

    def _load_all_by(self, by, version_number: Optional[str]) -> List[Entity]:
        from ..._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        r = []
        try:
            for f in self.dir_path.iterdir():
                if entity := self.model.__to_entity(f, by=by, version_number=version_number):
                    r.append(entity)
        except FileNotFoundError:
            pass
        return r

    def _delete(self, model_id: str):
        try:
            self.__get_model_filepath(model_id).unlink()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _delete_all(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def _delete_many(self, ids: Iterable[str]):
        for model_id in ids:
            self._delete(model_id)

    def _search(self, attribute: str, value: Any, version_number: Optional[str]) -> Optional[Entity]:
        return next(self.__search(attribute, value, version_number), None)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        if isinstance(folder_path, str):
            folder: pathlib.Path = pathlib.Path(folder_path)
        else:
            folder = folder_path

        if folder.resolve() == self._storage_folder.resolve():
            raise InvalidExportPath("The export folder must not be the storage folder.")

        export_dir = folder / self._dir_name
        if not export_dir.exists():
            export_dir.mkdir(parents=True)

        export_path = export_dir / f"{entity_id}.json"
        # Delete if exists.
        if export_path.exists():
            export_path.unlink()

        shutil.copy2(self.__get_model_filepath(entity_id), export_path)

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def __search(self, attribute: str, value: str, version_number: Optional[str] = None) -> Iterator[Entity]:
        return filter(lambda e: getattr(e, attribute, None) == value, self._load_all(version_number))

    def __get_model_filepath(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"
