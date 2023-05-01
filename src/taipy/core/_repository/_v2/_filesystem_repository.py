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
from typing import Any, Dict, Iterable, Iterator, List, Optional, Type, Union

from taipy.config.config import Config

from ...common._utils import _retry
from ...common.typing import Converter, Entity, Json, ModelType
from ...exceptions import InvalidExportPath, ModelNotFound
from .._v2._abstract_repository import _AbstractRepository
from .._v2._decoder import _Decoder
from .._v2._encoder import _Encoder


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

    def __init__(self, model: Type[ModelType], converter: Type[Converter], dir_name: str):
        self.model = model
        self.converter = converter
        self._dir_name = dir_name

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)

    ###############################
    # ##   Inherited methods   ## #
    ###############################
    def _save(self, entity: Entity):
        self.__create_directory_if_not_exists()
        model = self.converter._entity_to_model(entity)  # type: ignore
        self.__get_path(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_Encoder, check_circular=False)
        )

    @_retry(Config.global_config.read_entity_retry or 0, (Exception,))
    def _load(self, entity_id: str) -> Entity:
        try:
            with pathlib.Path(self.__get_path(entity_id)).open(encoding="UTF-8") as source:
                file_content = json.load(source)
            return self.__file_content_to_entity(file_content)
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), entity_id)

    @_retry(Config.global_config.read_entity_retry or 0, (Exception,))
    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
        if not filters:
            filters = []
        entities = []
        try:
            for f in self.dir_path.iterdir():
                if data := self.__filter_by(f, filters):
                    entities.append(self.__file_content_to_entity(data))
        except FileNotFoundError:
            pass
        return entities

    def _delete(self, entity_id: str):
        try:
            self.__get_path(entity_id).unlink()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), entity_id)

    def _delete_all(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def _delete_many(self, ids: Iterable[str]):
        for model_id in ids:
            self._delete(model_id)

    def _delete_by(self, attribute: str, value: str):
        while entity := self._search(attribute, value):
            self._delete(entity.id)  # type: ignore

    def _search(self, attribute: str, value: Any, filters: List[Dict] = None) -> Optional[Entity]:
        return next(self.__search(attribute, value), None)

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

        shutil.copy2(self.__get_path(entity_id), export_path)

    ###########################################
    # ##   Specific or optimized methods   ## #
    ###########################################
    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids, filters: List[Dict] = None):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        if not filters:
            filters = []
        res = {}
        configs_and_owner_ids = set(configs_and_owner_ids)

        try:
            for f in self.dir_path.iterdir():
                config_id, owner_id, entity = self.__match_file_and_get_entity(f, configs_and_owner_ids, filters)

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

    def _get_by_config_and_owner_id(
        self, config_id: str, owner_id: Optional[str], filters: List[Dict] = None
    ) -> Optional[Entity]:
        if not filters:
            filters = []
        if owner_id is not None:
            filters.append({"owner_id": owner_id})
        return self.__filter_files_by_config_and_owner_id(config_id, owner_id, filters)

    #############################
    # ##   Private methods   ## #
    #############################
    @_retry(Config.global_config.read_entity_retry or 0, (Exception,))
    def __filter_files_by_config_and_owner_id(
        self, config_id: str, owner_id: Optional[str], filters: List[Dict] = None
    ):
        try:
            files = filter(lambda f: config_id in f.name, self.dir_path.iterdir())
            entities = map(
                lambda f: self.__file_content_to_entity(self.__filter_by(f, filters)),
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

    @_retry(Config.global_config.read_entity_retry or 0, (Exception,))
    def __match_file_and_get_entity(self, filepath, config_and_owner_ids, filters):
        versions = [f'"version": "{item.get("version")}"' for item in filters if item.get("version")]

        filename = filepath.name

        if match := [(c, p) for c, p in config_and_owner_ids if c.id in filename]:
            with open(filepath, "r") as f:
                file_content = f.read()

            for config_id, owner_id in match:
                if not all(version in file_content for version in versions):
                    continue

                if owner_id and owner_id not in file_content:
                    continue

                entity = self.__file_content_to_entity(file_content)
                if entity.owner_id == owner_id and entity.config_id == config_id.id:
                    return config_id, owner_id, entity

        return None, None, None

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def __search(self, attribute: str, value: str, filters: List[Dict] = None) -> Iterator[Entity]:
        return filter(lambda e: getattr(e, attribute, None) == value, self._load_all(filters))

    def __get_path(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"

    def __file_content_to_entity(self, file_content):
        if not file_content:
            return None
        if isinstance(file_content, str):
            file_content = json.loads(file_content, cls=_Decoder)
        model = self.model.from_dict(file_content)
        entity = self.converter._model_to_entity(model)
        return entity

    def __filter_by(self, filepath: pathlib.Path, filters: Optional[List[Dict]]) -> Json:
        if not filters:
            filters = []
        with open(filepath, "r") as f:
            contents = f.read()
            for _filter in filters:
                if not all(f'"{key}": "{value}"' in contents for key, value in _filter.items()):
                    return None

        return json.loads(contents, cls=_Decoder)
