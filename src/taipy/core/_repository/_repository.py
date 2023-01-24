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
import re
from abc import abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generic, Iterable, List, Optional, TypeVar, Union

Json = Union[dict, list, str, int, float, bool, None]

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")


class _AbstractRepository(Generic[ModelType, Entity]):
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

    @abstractmethod
    def load(self, model_id: str) -> Entity:
        """
        Retrieve the entity data from the repository.

        Args:
            model_id: The entity id, i.e., its primary key.

        Returns:
            An entity.

        """
        raise NotImplementedError

    @abstractmethod
    def _load_all(self, version_number: Optional[str]) -> List[Entity]:
        """
        Retrieve all the entities' data from the repository of a specific version.

        Returns:
            A list of entities.
        """
        raise NotImplementedError

    @abstractmethod
    def _load_all_by(self, by, version_number: Optional[str]) -> List[Entity]:
        """
        Retrieve all the entities' data from the repository of a specific version
        based on a criteria.

        Returns:
            The list of all entities matching the criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def _save(self, entity: Entity):
        """
        Save an entity in the repository.

        Args:
            entity: The data from an object

        """
        raise NotImplementedError

    @abstractmethod
    def _delete(self, entity_id: str):
        """
        Delete an entity in the repository.

        Args:
            entity_id: The id of the entity to be deleted.

        """
        raise NotImplementedError

    @abstractmethod
    def _delete_all(self):
        """
        Delete all entities from the repository.
        """
        raise NotImplementedError

    @abstractmethod
    def _delete_many(self, ids: Iterable[str]):
        """
        Delete all entities from the list of ids from the repository.
        """
        raise NotImplementedError

    @abstractmethod
    def _search(self, attribute: str, value: Any, version_number: Optional[str]) -> Optional[Entity]:
        """
        Args:
            attribute: The entity property that is the key to the search.
            value: The value of the attribute that are being searched.
            version_number (Optional[str]): The version to search from.

        Returns:
            A list of entities

        """
        raise NotImplementedError

    @abstractmethod
    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        """
        Export an entity from the repository.

        Args:
            entity_id (str): The id of the entity to be exported.
            folder_path (Union[str, pathlib.Path]): The folder path to export the entity to.

        """
        raise NotImplementedError


def _timedelta_to_str(obj: timedelta) -> str:
    total_seconds = obj.total_seconds()
    return (
        f"{int(total_seconds // 86400)}d"
        f"{int(total_seconds % 86400 // 3600)}h"
        f"{int(total_seconds % 3600 // 60)}m"
        f"{int(total_seconds % 60)}s"
    )


def _str_to_timedelta(timedelta_str: str) -> timedelta:
    """
    Parse a time string e.g. (2h13m) into a timedelta object.

    :param timedelta_str: A string identifying a duration.  (eg. 2h13m)
    :return datetime.timedelta: A datetime.timedelta object
    """
    regex = re.compile(
        r"^((?P<days>[\.\d]+?)d)? *"
        r"((?P<hours>[\.\d]+?)h)? *"
        r"((?P<minutes>[\.\d]+?)m)? *"
        r"((?P<seconds>[\.\d]+?)s)?$"
    )
    parts = regex.match(timedelta_str)
    if not parts:
        raise TypeError("Can not deserialize string into timedelta")
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    # mypy has an issue with dynamic keyword parameters, hence the type ignore on the line bellow.
    return timedelta(**time_params)  # type: ignore


class _CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Json:
        if isinstance(o, Enum):
            result = o.value
        elif isinstance(o, datetime):
            result = {"__type__": "Datetime", "__value__": o.isoformat()}
        elif isinstance(o, timedelta):
            result = {"__type__": "Timedelta", "__value__": _timedelta_to_str(o)}
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class _CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        if source.get("__type__") == "Datetime":
            return datetime.fromisoformat(source.get("__value__"))
        if source.get("__type__") == "Timedelta":
            return _str_to_timedelta(source.get("__value__"))
        else:
            return source
