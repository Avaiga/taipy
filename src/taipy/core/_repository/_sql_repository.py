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

from sqlalchemy.dialects import sqlite
from sqlalchemy.exc import NoResultFound

from .._repository._abstract_repository import _AbstractRepository
from ..common.typing import Converter, Entity, ModelType
from ..exceptions import ModelNotFound
from .db._sql_connection import _SQLConnection


class _SQLRepository(_AbstractRepository[ModelType, Entity]):
    def __init__(self, model_type: Type[ModelType], converter: Type[Converter]):
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
        self.db = _SQLConnection.init_db()
        self.model_type = model_type
        self.converter = converter

    ###############################
    # ##   Inherited methods   ## #
    ###############################
    def _save(self, entity: Entity):
        obj = self.converter._entity_to_model(entity)
        if self._exists(entity.id):  # type: ignore
            self._update_entry(obj)
            return
        self.__insert_model(obj)

    def _exists(self, entity_id: str):
        query = self.model_type.__table__.select().filter_by(id=entity_id)  # type: ignore
        return bool(self.db.execute(str(query), [entity_id]).fetchone())

    def _load(self, entity_id: str) -> Entity:
        query = self.model_type.__table__.select().filter_by(id=entity_id)  # type: ignore

        if entry := self.db.execute(str(query.compile(dialect=sqlite.dialect())), [entity_id]).fetchone():
            entry = self.model_type.from_dict(entry)  # type: ignore
            return self.converter._model_to_entity(entry)
        raise ModelNotFound(str(self.model_type.__name__), entity_id)

    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.model_type.__table__.select()  # type: ignore
        entities: List[Entity] = []

        for f in filters or [{}]:
            filtered_query = query.filter_by(**f)
            try:
                entries = self.db.execute(
                    str(filtered_query.compile(dialect=sqlite.dialect())),
                    [self.__serialize_filter_values(val) for val in list(f.values())],
                ).fetchall()

                entities.extend(
                    [self.converter._model_to_entity(self.model_type.from_dict(m)) for m in entries]  # type: ignore
                )
            except NoResultFound:
                continue
        return entities

    def _delete(self, entity_id: str):
        delete_query = self.model_type.__table__.delete().filter_by(id=entity_id)  # type: ignore
        cursor = self.db.execute(str(delete_query.compile(dialect=sqlite.dialect())), [entity_id])
        self.db.commit()

        if cursor.rowcount == 0:
            raise ModelNotFound(str(self.model_type.__name__), entity_id)

        if cursor.rowcount == 0:
            raise ModelNotFound(str(self.model_type.__name__), entity_id)

    def _delete_all(self):
        self.db.execute(str(self.model_type.__table__.delete().compile(dialect=sqlite.dialect())))  # type: ignore
        self.db.commit()

    def _delete_many(self, ids: Iterable[str]):
        for entity_id in ids:
            self._delete(entity_id)

    def _delete_by(self, attribute: str, value: str):
        delete_by_query = self.model_type.__table__.delete().filter_by(**{attribute: value})  # type: ignore

        self.db.execute(str(delete_by_query.compile(dialect=sqlite.dialect())), [value])
        self.db.commit()

    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.model_type.__table__.select().filter_by(**{attribute: value})  # type: ignore

        entities: List[Entity] = []
        for f in filters or [{}]:
            entries = self.db.execute(
                str(query.filter_by(**f).compile(dialect=sqlite.dialect())),
                [value] + [self.__serialize_filter_values(val) for val in list(f.values())],
            ).fetchall()
            entities.extend(
                [self.converter._model_to_entity(self.model_type.from_dict(m)) for m in entries]  # type: ignore
            )

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

        query = self.model_type.__table__.select().filter_by(id=entity_id)  # type: ignore

        if entry := self.db.execute(str(query.compile(dialect=sqlite.dialect())), [entity_id]).fetchone():
            with open(export_path, "w", encoding="utf-8") as export_file:
                export_file.write(json.dumps(entry))
        else:
            raise ModelNotFound(self.model_type, entity_id)  # type: ignore

    ###########################################
    # ##   Specific or optimized methods   ## #
    ###########################################
    def _get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = self.model_type.__table__.select().offset(skip).limit(limit)  # type: ignore
        return self.db.execute(str(query.compile(dialect=sqlite.dialect()))).fetchall()

    def _get_by_config(self, config_id: Any) -> Optional[ModelType]:
        query = self.model_type.__table__.select().filter_by(config_id=config_id)  # type: ignore
        return self.db.execute(str(query.compile(dialect=sqlite.dialect())), [config_id]).fetchall()

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
        self, config_id: str, owner_id: Optional[str] = None, filters: Optional[List[Dict]] = None
    ) -> Optional[ModelType]:
        if not filters:
            filters = []
        versions = [item.get("version") for item in filters if item.get("version")]

        query = self.model_type.__table__.select().filter_by(config_id=config_id)  # type: ignore
        parameters = [config_id]

        if owner_id:
            parameters.append(owner_id)
        query = query.filter_by(owner_id=owner_id)
        query = str(query.compile(dialect=sqlite.dialect()))

        if versions:
            table_name = self.model_type.__table__.name  # type: ignore
            query = query + f" AND {table_name}.version IN ({','.join(['?']*len(versions))})"  # type: ignore
            parameters.extend(versions)  # type: ignore

        if entry := self.db.execute(query, parameters).fetchone():
            return self.model_type.from_dict(entry)  # type: ignore
        return None

    #############################
    # ##   Private methods   ## #
    #############################
    def __insert_model(self, model: ModelType):
        query = self.model_type.__table__.insert()  # type: ignore
        self.db.execute(str(query.compile(dialect=sqlite.dialect())), model.to_list(model))  # type: ignore
        self.db.commit()

    def _update_entry(self, model):
        query = self.model_type.__table__.update().filter_by(id=model.id)
        self.db.execute(str(query.compile(dialect=sqlite.dialect())), model.to_list(model) + [model.id])
        self.db.commit()

    @staticmethod
    def __serialize_filter_values(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value).replace('"', "'")
        return value
