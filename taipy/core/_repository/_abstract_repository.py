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
import pathlib
from abc import abstractmethod
from typing import Any, Dict, Generic, Iterable, List, Optional, TypeVar, Union

from ..exceptions import FileCannotBeRead
from ._decoder import _Decoder

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")


class _AbstractRepository(Generic[ModelType, Entity]):
    @abstractmethod
    def _save(self, entity: Entity):
        """
        Save an entity in the repository.

        Parameters:
            entity: The data from an object.
        """
        raise NotImplementedError

    @abstractmethod
    def _exists(self, entity_id: str) -> bool:
        """
        Check if an entity with id entity_id exists in the repository.
        Parameters:
            entity_id: The entity id, i.e., its primary key.

        Returns:
            True if the entity id exists.
        """
        raise NotImplementedError

    @abstractmethod
    def _load(self, entity_id: str) -> Entity:
        """
        Retrieve the entity data from the repository.
        Parameters:
            entity_id: The entity id, i.e., its primary key.

        Returns:
            An entity.
        """
        raise NotImplementedError

    @abstractmethod
    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
        """
        Retrieve all the entities' data from the repository taking any passed filter into account.

        Returns:
            A list of entities.
        """
        raise NotImplementedError

    @abstractmethod
    def _delete(self, entity_id: str):
        """
        Delete an entity in the repository.

        Parameters:
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

        Parameters:
            ids: List of ids to be deleted.
        """
        raise NotImplementedError

    @abstractmethod
    def _delete_by(self, attribute: str, value: str):
        """
        Delete all entities from the list of ids from the repository.

        Parameters:
            attribute: The entity property that is the key to the search.
            value: The value of the attribute that are being searched.
        """
        raise NotImplementedError

    @abstractmethod
    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[Entity]:
        """
        Parameters:
            attribute: The entity property that is the key to the search.
            value: The value of the attribute that are being searched.

        Returns:
            A list of entities that match the search criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        """
        Export an entity from the repository.

        Parameters:
            entity_id (str): The id of the entity to be exported.
            folder_path (Union[str, pathlib.Path]): The folder path to export the entity to.
        """
        raise NotImplementedError

    def _import(self, entity_file_path: pathlib.Path) -> Entity:
        """
        Import an entity from an exported file.

        Parameters:
            folder_path (Union[str, pathlib.Path]): The folder path to export the entity to.

        Returns:
            The imported entity.
        """
        if not entity_file_path.is_file():
            raise FileNotFoundError

        try:
            with entity_file_path.open("r", encoding="UTF-8") as f:
                file_content = f.read()
        except Exception:
            raise FileCannotBeRead(str(entity_file_path)) from None

        if isinstance(file_content, str):
            file_content = json.loads(file_content, cls=_Decoder)
        model = self.model_type.from_dict(file_content)  # type: ignore[attr-defined]
        return self.converter._model_to_entity(model)  # type: ignore[attr-defined]
