from typing import Any, Generic, List, TypeVar, Union

from taipy.core.common.logger import TaipyLogger
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.repository import FileSystemRepository

EntityType = TypeVar("EntityType")


class Manager(Generic[EntityType]):
    _repository: FileSystemRepository
    _logger = TaipyLogger.get_logger()
    ENTITY_NAME: str = "Entity"

    @classmethod
    def delete_all(cls):
        """
        Deletes all entities.
        """
        cls._repository.delete_all()

    @classmethod
    def delete(cls, id: Any, *args: Any, **kwargs: Any):
        """
        Deletes an entity by id.
        """
        cls._repository.delete(id)

    @classmethod
    def set(cls, entity: EntityType):
        """
        Save or update an entity.
        """
        cls._repository.save(entity)

    @classmethod
    def get_all(cls) -> List[EntityType]:
        """
        Returns all entities.
        """
        return cls._repository.load_all()

    @classmethod
    def get(cls, entity: Union[str, EntityType], default=None, *args: Any, **kwargs: Any) -> EntityType:
        """
        Returns an entity by id or reference.
        """
        entity_id = entity if isinstance(entity, str) else entity.id  # type: ignore
        try:
            return cls._repository.load(entity_id)
        except ModelNotFound:
            cls._logger.error(f"{cls.ENTITY_NAME} not found: {entity_id}")
            return default
