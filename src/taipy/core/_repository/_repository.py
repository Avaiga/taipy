from typing import Type, TypeVar, Generic, List, Any
from abc import abstractmethod, ABC


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
    def _delete_many(self, ids: List[str]):
        """
        Delete all entities from the list of ids from the repository.
        """
        raise NotImplementedError

    @abstractmethod
    def _search(self, attribute: str, value: Any) -> List[Entity]:
        """
        Args:
            attribute: The entity property that is the key to the search.
            value: The value of the attribute that are being searched.

        Returns: A list of entities

        """
        raise NotImplementedError

    @abstractmethod
    def _foo(self):
        """
        Returns:
        """
        raise NotImplementedError
