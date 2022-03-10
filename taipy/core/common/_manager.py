from typing import Any, Generic, List, TypeVar, Union

from taipy.core._repository import _FileSystemRepository
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.exceptions.exceptions import ModelNotFound

EntityType = TypeVar("EntityType")


class _Manager(Generic[EntityType]):
    _repository: _FileSystemRepository
    _logger = _TaipyLogger._get_logger()
    _ENTITY_NAME: str = "Entity"

    @classmethod
    def _delete_all(cls):
        """
        Deletes all entities.
        """
        cls._repository._delete_all()

    @classmethod
    def _delete(cls, id: Any, *args: Any, **kwargs: Any):
        """
        Deletes an entity by id.
        """
        cls._repository._delete(id)

    @classmethod
    def _set(cls, entity: EntityType):
        """
        Save or update an entity.
        """
        cls._repository._save(entity)

    @classmethod
    def _get_all(cls) -> List[EntityType]:
        """
        Returns all entities.
        """
        return cls._repository._load_all()

    @classmethod
    def _get(cls, entity: Union[str, EntityType], default=None, *args: Any, **kwargs: Any) -> EntityType:
        """
        Returns an entity by id or reference.
        """
        entity_id = entity if isinstance(entity, str) else entity.id  # type: ignore
        try:
            return cls._repository.load(entity_id)
        except ModelNotFound:
            cls._logger.error(f"{cls._ENTITY_NAME} not found: {entity_id}")
            return default
