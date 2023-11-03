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
import sqlite3
from typing import Any, Dict, Iterable, List, Optional, Type, Union

from sqlalchemy.dialects import sqlite
from sqlalchemy.exc import NoResultFound
from sqlalchemy.schema import CreateTable

from taipy.config.config import Config

from .._repository._abstract_repository import _AbstractRepository
from .._repository.db._sql_session import _SQLSession
from ..common.typing import Converter, Entity, ModelType
from ..exceptions import MissingRequiredProperty, ModelNotFound

connection = None


from taipy.config.config import Config

from .._repository._abstract_repository import _AbstractRepository
from .._repository.db._sql_session import _SQLSession
from ..exceptions import MissingRequiredProperty, ModelNotFound

connection = None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db():
    properties = Config.core.repository_properties
    try:
        db_location = properties["db_location"]
    except KeyError:
        raise MissingRequiredProperty("Missing property db_location")

    sqlite3.threadsafety = 3

    global connection
    connection = connection if connection else sqlite3.connect(db_location, check_same_thread=False)
    connection.row_factory = dict_factory

    from .._version._version_model import _VersionModel
    from ..cycle._cycle_model import _CycleModel
    from ..data._data_model import _DataNodeModel
    from ..job._job_model import _JobModel
    from ..scenario._scenario_model import _ScenarioModel
    from ..task._task_model import _TaskModel

    connection.execute(str(CreateTable(_CycleModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
    connection.execute(str(CreateTable(_DataNodeModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
    connection.execute(str(CreateTable(_JobModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
    connection.execute(str(CreateTable(_ScenarioModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
    connection.execute(str(CreateTable(_TaskModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
    connection.execute(str(CreateTable(_VersionModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))

    return connection


class _SQLRepository(_AbstractRepository[ModelType, Entity]):
    def __init__(self, model_type: Type[ModelType], converter: Type[Converter], session=None):
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
        self.db = init_db()
        self.model_type = model_type
        self.converter = converter

    ###############################
    # ##   Inherited methods   ## #
    ###############################
    def _save(self, entity: Entity):
        obj = self.converter._entity_to_model(entity)
        if self._exists(entity.id):
            self._update_entry(obj)
            return
        self.__insert_model(obj)

    def _exists(self, entity_id: str):
        return bool(
            self.db.execute(str(self.model_type.__table__.select().filter_by(id=entity_id)), [entity_id]).fetchone()
        )

    def _load(self, entity_id: str) -> Entity:
        get_query = str(self.model_type.__table__.select().filter_by(id=entity_id).compile(dialect=sqlite.dialect()))

        if entry := self.db.execute(str(get_query), [entity_id]).fetchone():  # type: ignore
            entry = self.model_type.from_dict(entry)
            return self.converter._model_to_entity(entry)
        raise ModelNotFound(str(self.model_type.__name__), entity_id)

    @staticmethod
    def serialize_filter_values(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value).replace('"', "'")
        return value

    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.model_type.__table__.select()
        entities: List[Entity] = []

        for f in filters or [{}]:
            filtered_query = query.filter_by(**f)
            try:
                entries = self.db.execute(
                    str(filtered_query.compile(dialect=sqlite.dialect())),
                    [self.serialize_filter_values(val) for val in list(f.values())],
                ).fetchall()

                entities.extend([self.converter._model_to_entity(self.model_type.from_dict(m)) for m in entries])
            except NoResultFound:
                continue
        return entities

    def _delete(self, entity_id: str):
        delete_query = self.model_type.__table__.delete().filter_by(id=entity_id).compile(dialect=sqlite.dialect())
        cursor = self.db.execute(str(delete_query), [entity_id])
        self.db.commit()

        if cursor.rowcount == 0:
            raise ModelNotFound(str(self.model_type.__name__), entity_id)

        if cursor.rowcount == 0:
            raise ModelNotFound(str(self.model_type.__name__), entity_id)

    def _delete_all(self):
        self.db.execute(str(self.model_type.__table__.delete().compile(dialect=sqlite.dialect())))
        self.db.commit()

    def _delete_many(self, ids: Iterable[str]):
        for entity_id in ids:
            self._delete(entity_id)

    def _delete_by(self, attribute: str, value: str):
        delete_by_query = (
            self.model_type.__table__.delete().filter_by(**{attribute: value}).compile(dialect=sqlite.dialect())
        )
        self.db.execute(str(delete_by_query), [value])
        self.db.commit()

    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[Entity]:
        query = self.model_type.__table__.select().filter_by(**{attribute: value})

        entities: List[Entity] = []
        for f in filters or [{}]:
            entries = self.db.execute(
                str(query.filter_by(**f).compile(dialect=sqlite.dialect())),
                [value] + [self.serialize_filter_values(val) for val in list(f.values())],
            ).fetchall()
            entities.extend([self.converter._model_to_entity(self.model_type.from_dict(m)) for m in entries])

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

        get_query = str(self.model_type.__table__.select().filter_by(id=entity_id).compile(dialect=sqlite.dialect()))

        if entry := self.db.execute(str(get_query), [entity_id]).fetchone():  # type: ignore
            with open(export_path, "w", encoding="utf-8") as export_file:
                export_file.write(json.dumps(entry))
        else:
            raise ModelNotFound(self.model_type, entity_id)  # type: ignore

    ###########################################
    # ##   Specific or optimized methods   ## #
    ###########################################
    def _get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = str(self.model_type.__table__.select().offset(skip).limit(limit).compile(dialect=sqlite.dialect()))
        return self.db.execute(query).fetchall()

    def _get_by_config(self, config_id: Any) -> Optional[ModelType]:
        query = str(self.model_type.__table__.select().filter_by(config_id=config_id).compile(dialect=sqlite.dialect()))
        return self.db.execute(query, [config_id]).fetchall()

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
    ) -> ModelType:
        if not filters:
            filters = []
        versions = [item.get("version") for item in filters if item.get("version")]

        query = self.model_type.__table__.select().filter_by(config_id=config_id)
        parameters = [config_id]

        if owner_id:
            parameters.append(owner_id)
        query = query.filter_by(owner_id=owner_id)
        query = str(query.compile(dialect=sqlite.dialect()))

        if versions:

            query = query + f" AND {self.model_type.__table__.name}.version IN ({','.join(['?']*len(versions))})"
            # query = str(query.filter(self.model_type.version.in_(versions)).compile(dialect=sqlite.dialect()))  # type: ignore
            parameters.extend(versions)

        if entry := self.db.execute(query, parameters).fetchone():
            return self.model_type.from_dict(entry)
        return None

    #############################
    # ##   Private methods   ## #
    #############################
    def __insert_model(self, model: ModelType):
        query = str(self.model_type.__table__.insert().compile(dialect=sqlite.dialect()))
        self.db.execute(query, model.to_list(model))
        self.db.commit()

    def _update_entry(self, model):
        query = str(self.model_type.__table__.update().filter_by(id=model.id).compile(dialect=sqlite.dialect()))
        self.db.execute(query, model.to_list(model) + [model.id])
        self.db.commit()
