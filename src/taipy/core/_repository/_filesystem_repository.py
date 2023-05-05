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
import time
from abc import abstractmethod
from typing import Callable, Iterable, Iterator, List, Optional, Type, TypeVar, Union

from taipy.config.config import Config

from ..exceptions.exceptions import InvalidExportPath, ModelNotFound
from ._repository import _AbstractRepository, _CustomDecoder, _CustomEncoder

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")
Json = Union[dict, list, str, int, float, bool, None]


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

    @abstractmethod
    def _to_model(self, obj):
        """
        Converts the object to be saved to its model.
        """
        ...

    @abstractmethod
    def _from_model(self, model):
        """
        Converts a model to its functional object.
        """
        ...

    def __init__(self, model: Type[ModelType], dir_name: str, to_model_fct: Callable, from_model_fct: Callable):
        self.model = model
        self._dir_name = dir_name
        self._to_model = to_model_fct  # type: ignore
        self._from_model = from_model_fct  # type: ignore

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    def load(self, model_id: str) -> Entity:
        try:
            return self.__to_entity(
                self._get_model_filepath(model_id), retry=Config.global_config.read_entity_retry or 0
            )  # type: ignore
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[Entity]:
        """
        Load all entities from a specific version.
        """
        from .._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        r = []
        try:
            for f in self.dir_path.iterdir():
                if entity := self.__to_entity(
                    f, retry=Config.global_config.read_entity_retry or 0, version_number=version_number
                ):
                    r.append(entity)
        except FileNotFoundError:
            pass
        return r

    def _load_all_by(self, by, version_number: Optional[str] = None):
        from .._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        r = []
        try:
            for f in self.dir_path.iterdir():
                if entity := self.__to_entity(f, by=by, version_number=version_number):
                    r.append(entity)
        except FileNotFoundError:
            pass
        return r

    def _save(self, entity):
        self.__create_directory_if_not_exists()

        model = self._to_model(entity)
        self._get_model_filepath(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_CustomEncoder, check_circular=False)
        )

    def _delete_all(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def _delete(self, model_id: str):
        try:
            self._get_model_filepath(model_id).unlink()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _delete_many(self, model_ids: Iterable[str]):
        for model_id in model_ids:
            self._delete(model_id)

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        while entity := self._search(attribute, value, version_number):
            self._delete(entity.id)  # type: ignore

    def _search(self, attribute: str, value: str, version_number: Optional[str] = None) -> Optional[Entity]:
        return next(self.__search(attribute, value, version_number), None)

    def _get_by_config_id(self, config_id: str) -> List[Entity]:
        entities: List[Entity] = []
        for f in filter(lambda f: config_id in f.name, self.dir_path.iterdir()):
            if entity := self.__to_entity(f, retry=Config.global_config.read_entity_retry or 0):
                entities.append(entity)
        return entities

    def _get_by_config_and_owner_id(self, config_id: str, owner_id: Optional[str]) -> Optional[Entity]:
        # Only get the entity from the latest version
        from .._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(None)

        try:
            files = filter(lambda f: config_id in f.name, self.dir_path.iterdir())
            entities = map(
                lambda f: self.__to_entity(
                    f, by=owner_id, version_number=version_number, retry=Config.global_config.read_entity_retry or 0
                ),
                files,
            )
            corresponding_entities = filter(
                lambda e: e is not None and e.config_id == config_id and e.owner_id == owner_id,  # type: ignore
                entities,
            )
            return next(corresponding_entities, None)  # type: ignore
        except FileNotFoundError:
            pass
        return None

    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        res = {}
        configs_and_owner_ids = set(configs_and_owner_ids)

        try:
            for f in self.dir_path.iterdir():
                config_id, owner_id, entity = self.__match_file_and_get_entity(
                    f, configs_and_owner_ids, retry=Config.global_config.read_entity_retry or 0
                )

                if entity:
                    key = config_id, owner_id
                    res[key] = entity
                    configs_and_owner_ids.remove(key)

                    if len(configs_and_owner_ids) == 0:
                        return res
        except FileNotFoundError:
            # Folder with data was not created yet.
            return {}

        return res

    def _get_model_filepath(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"

    def __search(self, attribute: str, value: str, version_number: Optional[str] = None) -> Iterator[Entity]:
        return filter(lambda e: getattr(e, attribute, None) == value, self._load_all(version_number))

    def __to_entity(
        self,
        filepath,
        by: Union[Optional[str], List[Optional[str]]] = None,
        version_number: Union[Optional[str], List[Optional[str]]] = None,
        retry: Optional[int] = 0,
    ) -> Optional[Entity]:
        if not isinstance(by, List):
            by = [by] if by else []

        if not isinstance(version_number, List):
            version_number = [version_number] if version_number else []

        by_version = list(map(lambda version: f'"version": "{version}"', version_number) if version_number else [""])

        try:
            with open(filepath, "r") as f:
                file_content = f.read()

            if by or by_version:
                if all(criteria in file_content for criteria in by if criteria) and any(
                    version in file_content for version in by_version
                ):
                    return self.__model_to_entity(file_content)
                else:
                    return None

            return self.__model_to_entity(file_content)

        except Exception as e:
            if retry and retry > 0:
                time.sleep(0.5)
                return self.__to_entity(filepath, by=by, version_number=version_number, retry=retry - 1)
            raise e

    def __model_to_entity(self, file_content):
        data = json.loads(file_content, cls=_CustomDecoder)
        model = self.model.from_dict(data)  # type: ignore
        entity = self._from_model(model)
        # Add version attribute on old entities. Used to migrate from <=2.0 to >=2.1 version.
        # To be removed on later versions
        if not data.get("version") and hasattr(entity, "version"):
            self._save(entity)
            from taipy.logger._taipy_logger import _TaipyLogger

            _TaipyLogger._get_logger().warning(
                f"Entity {entity.id} has automatically been assigned to version named " f"{entity.version}"
            )
        return entity

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def __match_file_and_get_entity(self, filepath, config_and_owner_ids, retry: Optional[int] = 0):
        # Only get the entity from the latest version
        from .._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(None)

        if not isinstance(version_number, List):
            version_number = [version_number] if version_number else []
        version_number = [f'"version": "{version}"' for version in version_number]

        filename = filepath.name

        if match := [(c, p) for c, p in config_and_owner_ids if c.id in filename]:
            try:
                with open(filepath, "r") as f:
                    file_content = f.read()

                for config_id, owner_id in match:
                    if not all(version in file_content for version in version_number):
                        continue

                    if owner_id and owner_id not in file_content:
                        continue

                    entity = self.__model_to_entity(file_content)
                    if entity.owner_id == owner_id and entity.config_id == config_id.id:
                        return config_id, owner_id, entity
            except Exception as e:
                if retry and retry > 0:
                    return self.__match_file_and_get_entity(filepath, config_and_owner_ids, retry=retry - 1)
                raise e

        return None, None, None

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

        shutil.copy2(self._get_model_filepath(entity_id), export_path)
