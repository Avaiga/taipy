# Copyright 2022 Avaiga Private Limited
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
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Iterable, Iterator, List, Optional, Type, TypeVar, Union

from taipy.config.config import Config

from ..exceptions.exceptions import ModelNotFound

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")
Json = Union[dict, list, str, int, float, bool, None]


class _CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Json:
        if isinstance(o, Enum):
            result = o.value
        elif isinstance(o, datetime):
            result = {"__type__": "Datetime", "__value__": o.isoformat()}
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class _CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        if source.get("__type__") == "Datetime":
            return datetime.fromisoformat(source.get("__value__"))
        else:
            return source


class _FileSystemRepository(Generic[ModelType, Entity]):
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

    @property
    @abstractmethod
    def _storage_folder(self) -> pathlib.Path:
        """
        Base folder used by _repository to store data
        """
        ...

    @abstractmethod
    def _from_model(self, model):
        """
        Converts a model to its functional object.
        """
        ...

    def __init__(self, model: Type[ModelType], dir_name: str):
        self.model = model
        self._dir_name = dir_name

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    def load(self, model_id: str) -> Entity:
        try:
            return self.__to_entity(
                self.__get_model_filepath(model_id), retry=Config.global_config.read_entity_retry or 0
            )  # type: ignore
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _load_all(self) -> List[Entity]:
        try:
            return [self.__to_entity(f, retry=Config.global_config.read_entity_retry or 0) for f in self.dir_path.iterdir()]  # type: ignore
        except FileNotFoundError:
            return []

    def _load_all_by(self, by):
        r = []
        try:
            for f in self.dir_path.iterdir():
                if entity := self.__to_entity(f, by=by):
                    r.append(entity)
        except FileNotFoundError:
            pass
        return r

    def _save(self, entity):
        self.__create_directory_if_not_exists()

        model = self._to_model(entity)
        self.__get_model_filepath(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_CustomEncoder, check_circular=False)
        )

    def _delete_all(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def _delete(self, model_id: str):
        try:
            self.__get_model_filepath(model_id).unlink()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _delete_many(self, model_ids: Iterable[str]):
        for model_id in model_ids:
            self._delete(model_id)

    def _search(self, attribute: str, value: str) -> Optional[Entity]:
        return next(self.__search(attribute, value), None)

    def _get_by_config_and_parent_id(self, config_id: str, parent_id: Optional[str]) -> Optional[Entity]:
        try:
            files = filter(lambda f: config_id in f.name, self.dir_path.iterdir())
            entities = map(
                lambda f: self.__to_entity(f, by=parent_id, retry=Config.global_config.read_entity_retry or 0), files
            )
            corresponding_entities = filter(
                lambda e: e is not None and e.config_id == config_id and e.parent_id == parent_id, entities  # type: ignore
            )
            return next(corresponding_entities, None)
        except FileNotFoundError:
            pass
        return None

    def _get_by_configs_and_parent_ids(self, configs_and_parent_ids):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        res = {}
        configs_and_parent_ids = set(configs_and_parent_ids)

        try:
            for f in self.dir_path.iterdir():
                config_id, parent_id, entity = self.__match_file_and_get_entity(
                    f, configs_and_parent_ids, retry=Config.global_config.read_entity_retry or 0
                )

                if entity:
                    key = config_id, parent_id
                    res[key] = entity
                    configs_and_parent_ids.remove(key)

                    if len(configs_and_parent_ids) == 0:
                        return res
        except FileNotFoundError:
            # Folder with data was not created yet.
            return {}

        return res

    def __search(self, attribute: str, value: str) -> Iterator[Entity]:
        return filter(lambda e: getattr(e, attribute, None) == value, self._load_all())

    def __get_model_filepath(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"

    def __to_entity(self, filepath, by: Optional[str] = None, retry: Optional[int] = 0) -> Entity:
        try:
            with open(filepath, "r") as f:
                file_content = f.read()

            if by:
                return self.__model_to_entity(file_content) if by in file_content else None

            return self.__model_to_entity(file_content)
        except Exception as e:
            if retry and retry > 0:
                time.sleep(0.5)
                return self.__to_entity(filepath, by=by, retry=retry - 1)
            raise e

    def __model_to_entity(self, file_content):
        data = json.loads(file_content, cls=_CustomDecoder)
        model = self.model.from_dict(data)  # type: ignore
        return self._from_model(model)

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def __match_file_and_get_entity(self, filepath, config_and_parent_ids, retry: Optional[int] = 0):
        filename = filepath.name

        if match := [(c, p) for c, p in config_and_parent_ids if c.id in filename]:
            try:
                with open(filepath, "r") as f:
                    file_content = f.read()

                for config_id, parent_id in match:
                    if parent_id and parent_id not in file_content:
                        continue

                    entity = self.__model_to_entity(file_content)
                    if entity.parent_id == parent_id and entity.config_id == config_id.id:
                        return config_id, parent_id, entity
            except Exception as e:
                if retry and retry > 0:
                    return self.__match_file_and_get_entity(filepath, config_and_parent_ids, retry=retry - 1)
                raise e

        return None, None, None
