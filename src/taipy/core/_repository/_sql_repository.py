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
from typing import Any, Dict, Iterable, List, Optional, Type, Union

from sqlalchemy.exc import NoResultFound

from ..common.typing import Converter, Entity, ModelType
from ..exceptions import ModelNotFound
from ._abstract_repository import _AbstractRepository
from .db._init_db import init_db
from .db._sql_session import SessionLocal


class _SQLRepository(_AbstractRepository[ModelType, Entity]):
    def __init__(self, model_type: Type[ModelType], converter: Type[Converter], session=SessionLocal()):
        """
        Holds common methods to be used and extended when the need for saving
        dataclasses in a SqlLite database.

        Some lines have type: ignore because MyPy won't recognize some generic attributes. This
        should be revised in the future.

        Attributes:
            model_type: Generic dataclass.
            converter: A class that handles conversion to and from a database backend
            db: An SQLAlchemy session object
        """
        self.model_type = model_type
        self.db = session
        self.converter = converter
        init_db()

    ###############################
    # ##   Inherited methods   ## #
    ###############################
    def _save(self, entity: Entity):
        obj = self.converter._entity_to_model(entity)
        if self.db.query(self.model_type).filter_by(id=obj.id).first():
            self.__update_entry(obj)
            return
        self.__insert_model(obj)

    def _exists(self, entity_id: str):
        return bool(self.db.query(self.model_type.id).filter_by(id=entity_id).first())  # type: ignore

    def _load(self, entity_id: str) -> Entity:
        if entry := self.db.query(self.model_type).filter(self.model_type.id == entity_id).first():  # type: ignore
            return self.converter._model_to_entity(entry)
        raise ModelNotFound(str(self.model_type.__name__), entity_id)

    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.db.query(self.model_type)
        entities: List[Entity] = []

        for f in filters or [{}]:
            filtered_query = query.filter_by(**f)
            try:
                entities.extend([self.converter._model_to_entity(m) for m in filtered_query.all()])
            except NoResultFound:
                continue
        return entities

    def _delete(self, entity_id: str):
        number_of_deleted_entries = self.db.query(self.model_type).filter_by(id=entity_id).delete()
        if not number_of_deleted_entries:
            raise ModelNotFound(str(self.model_type.__name__), entity_id)
        self.db.commit()

    def _delete_all(self):
        self.db.query(self.model_type).delete()
        self.db.commit()

    def _delete_many(self, ids: Iterable[str]):
        for entity_id in ids:
            self._delete(entity_id)

    def _delete_by(self, attribute: str, value: str):
        self.db.query(self.model_type).filter_by(**{attribute: value}).delete()

    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.db.query(self.model_type).filter_by(**{attribute: value})

        entities: List[Entity] = []
        for f in filters or [{}]:
            filtered_query = query.filter_by(**f)
            entities.extend([self.converter._model_to_entity(m) for m in filtered_query.all()])

        return entities

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        if isinstance(folder_path, str):
            folder: pathlib.Path = pathlib.Path(folder_path)
        else:
            folder = folder_path

        export_dir = folder / self.model_type.__table__.name  # type: ignore
        if not export_dir.exists():
            export_dir.mkdir(parents=True)

        export_path = export_dir / f"{entity_id}.json"

        entry = self.db.query(self.model_type).filter_by(id=entity_id).first()
        if entry is None:
            raise ModelNotFound(self.model_type, entity_id)  # type: ignore

        with open(export_path, "w", encoding="utf-8") as export_file:
            export_file.write(json.dumps(entry.to_dict()))

    ###########################################
    # ##   Specific or optimized methods   ## #
    ###########################################
    def _get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model_type).offset(skip).limit(limit).all()

    def _get_by_config(self, config_id: Any) -> Optional[ModelType]:
        return self.db.query(self.model_type).filter(self.model_type.config_id == config_id).first()  # type: ignore

    def _get_by_config_and_owner_id(
        self, config_id: str, owner_id: Optional[str], filters: Optional[List[Dict]] = None
    ) -> Optional[Entity]:
        if not filters:
            filters = [{}]
        if entry := self.__get_entities_by_config_and_owner(config_id, owner_id, filters):
            return self.converter._model_to_entity(entry)
        return None

    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids, filters: Optional[List[Dict]] = None):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        if not filters:
            filters = [{}]
        res = {}
        configs_and_owner_ids = set(configs_and_owner_ids)

        for config, owner in configs_and_owner_ids:
            entry = self.__get_entities_by_config_and_owner(config.id, owner, filters)
            if entry:
                entity = self.converter._model_to_entity(entry)
                key = config, owner
                res[key] = entity

        return res

    def __get_entities_by_config_and_owner(
        self, config_id: str, owner_id: Optional[str] = "", filters: Optional[List[Dict]] = None
    ) -> ModelType:
        if not filters:
            filters = []
        versions = [item.get("version") for item in filters if item.get("version")]
        if owner_id:
            query = self.db.query(self.model_type).filter_by(config_id=config_id).filter_by(owner_id=owner_id)
        else:
            query = self.db.query(self.model_type).filter_by(config_id=config_id).filter_by(owner_id=None)
        if versions:
            query = query.filter(self.model_type.version.in_(versions))  # type: ignore
        return query.first()

    #############################
    # ##   Private methods   ## #
    #############################
    def __insert_model(self, model: ModelType):
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

    def __update_entry(self, model):
        self.db.merge(model)
        self.db.commit()
