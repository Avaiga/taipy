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

import copy
import json
import pathlib
import shutil
from typing import Any, Dict, Iterable, Iterator, List, Optional, Type, Union

from taipy.config.config import Config

from ..common._utils import _retry_read_entity
from ..common.typing import Converter, Entity, Json, ModelType
from ..exceptions import FileCannotBeRead, InvalidExportPath, ModelNotFound
from ._abstract_repository import _AbstractRepository
from ._decoder import _Decoder
from ._encoder import _Encoder


class _FileSystemRepository(_AbstractRepository[ModelType, Entity]):
    """
    Holds common methods to be used and extended when the need for saving
    dataclasses as JSON files in local storage emerges.

    Some lines have type: ignore because MyPy won't recognize some generic attributes. This
    should be revised in the future.

    Attributes:
        model_type (ModelType): Generic dataclass.
        converter: A class that handles conversion to and from a database backend
        dir_name (str): Folder that will hold the files for this dataclass model.
    """

    __EXCEPTIONS_TO_RETRY = (FileCannotBeRead,)

    def __init__(self, model_type: Type[ModelType], converter: Type[Converter], dir_name: str):
        self.model_type = model_type
        self.converter = converter
        self._dir_name = dir_name

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.core.storage_folder)

    ###############################
    # ##   Inherited methods   ## #
    ###############################

    def _save(self, entity: Entity):
        self.__create_directory_if_not_exists()
        model = self.converter._entity_to_model(entity)  # type: ignore
        self.__get_path(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_Encoder, check_circular=False)
        )

    def _exists(self, entity_id: str) -> bool:
        return self.__get_path(entity_id).exists()

    def _load(self, entity_id: str) -> Entity:
        path = pathlib.Path(self.__get_path(entity_id))

        try:
            file_content = self.__read_file(path)
        except (FileNotFoundError, FileCannotBeRead):
            raise ModelNotFound(str(self.dir_path), entity_id)

        return self.__file_content_to_entity(file_content)

    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
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
        filters: List[Dict] = [{}]
        for fil in filters:
            fil.update({attribute: value})

        try:
            for f in self.dir_path.iterdir():
                if self.__filter_by(f, filters):
                    f.unlink()
        except FileNotFoundError:
            pass

    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[Entity]:
        return list(self.__search(attribute, value, filters))

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
    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids, filters: Optional[List[Dict]] = None):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        if not filters:
            filters = [{}]
        res = {}
        configs_and_owner_ids = set(configs_and_owner_ids)

        try:
            for f in self.dir_path.iterdir():
                config_id, owner_id, entity = self.__match_file_and_get_entity(
                    f, configs_and_owner_ids, copy.deepcopy(filters)
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

    def _get_by_config_and_owner_id(
        self, config_id: str, owner_id: Optional[str], filters: Optional[List[Dict]] = None
    ) -> Optional[Entity]:
        if not filters:
            filters = [{}]
        else:
            filters = copy.deepcopy(filters)

        if owner_id is not None:
            for fil in filters:
                fil.update({"owner_id": owner_id})
        return self.__filter_files_by_config_and_owner_id(config_id, owner_id, filters)

    #############################
    # ##   Private methods   ## #
    #############################

    def __filter_files_by_config_and_owner_id(
        self, config_id: str, owner_id: Optional[str], filters: Optional[List[Dict]] = None
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

    def __match_file_and_get_entity(self, filepath, config_and_owner_ids, filters):
        if match := [(c, p) for c, p in config_and_owner_ids if c.id in filepath.name]:
            for config, owner_id in match:
                for fil in filters:
                    fil.update({"config_id": config.id, "owner_id": owner_id})

                if data := self.__filter_by(filepath, filters):
                    return config, owner_id, self.__file_content_to_entity(data)

        return None, None, None

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def __search(self, attribute: str, value: str, filters: Optional[List[Dict]] = None) -> Iterator[Entity]:
        return filter(lambda e: getattr(e, attribute, None) == value, self._load_all(filters))

    def __get_path(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"

    def __file_content_to_entity(self, file_content):
        if not file_content:
            return None
        if isinstance(file_content, str):
            file_content = json.loads(file_content, cls=_Decoder)
        model = self.model_type.from_dict(file_content)
        entity = self.converter._model_to_entity(model)
        return entity

    def __filter_by(self, filepath: pathlib.Path, filters: Optional[List[Dict]]) -> Optional[Json]:
        if not filters:
            filters = [{}]

        try:
            file_content = self.__read_file(filepath)
        except (FileNotFoundError, FileCannotBeRead):
            return None

        for _filter in filters:
            conditions = [
                f'"{key}": "{value}"' if value is not None else f'"{key}": null' for key, value in _filter.items()
            ]
            if all(condition in file_content for condition in conditions):
                return json.loads(file_content, cls=_Decoder)
        return None

    @_retry_read_entity(__EXCEPTIONS_TO_RETRY)
    def __read_file(self, filepath: pathlib.Path) -> str:
        if not filepath.is_file():
            raise FileNotFoundError

        try:
            with filepath.open("r", encoding="UTF-8") as f:
                file_content = f.read()
            return file_content
        except Exception:
            raise FileCannotBeRead(str(filepath))
