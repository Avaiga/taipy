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

from abc import abstractmethod
from typing import Any, Generic, Iterable, List, Optional, TypeVar

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")


class _AbstractRepository(Generic[ModelType, Entity]):
    @abstractmethod
    def load(self, model_id: str) -> Entity:
        """
        Retrieve the entity data from the repository.

        Args:
            model_id: The entity id, i.e., its primary key.

        Returns: An entity.

        """
        raise NotImplementedError

    @abstractmethod
    def _load_all(self) -> List[Entity]:
        """
        Retrieve all the entities' data from the repository.

        Returns: A list of entities.
        """
        raise NotImplementedError

    @abstractmethod
    def _load_all_by(self, by) -> List[Entity]:
        """
        Retrieve all the entities' data from the repository based
        on a criteria.

        Returns: A list of entities.
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
    def _search(self, attribute: str, value: Any) -> Optional[Entity]:
        """
        Args:
            attribute: The entity property that is the key to the search.
            value: The value of the attribute that are being searched.

        Returns: A list of entities

        """
        raise NotImplementedError
