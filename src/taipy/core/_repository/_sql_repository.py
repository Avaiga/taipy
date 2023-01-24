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
from abc import abstractmethod
from typing import Any, Callable, Iterable, List, Optional, Type, TypeVar, Union

from sqlalchemy import create_engine, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taipy.config.config import Config

from ..exceptions.exceptions import MissingRequiredProperty, ModelNotFound, VersionIsNotProductionVersion
from ._repository import _AbstractRepository, _CustomDecoder, _CustomEncoder
from ._sql_model import Base, _TaipyModel, _TaipyVersion

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")


class _BaseSQLRepository(_AbstractRepository[ModelType, Entity]):
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

    def __init__(self):
        properties = Config.global_config.repository_properties
        try:
            # More sql databases can be easily added in the future
            self.engine = create_engine(
                f"sqlite:///{properties.get('db_location')}?check_same_thread=False", poolclass=StaticPool
            )

            # Maybe this should be in the taipy package? So it's not executed every time
            # the class is instantiated
            Base.metadata.create_all(self.engine)
            _session = sessionmaker(bind=self.engine)
            self.session = _session()

        except KeyError:
            raise MissingRequiredProperty("Missing property db_location")


class _TaipyModelTable(_BaseSQLRepository[ModelType, Entity]):
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

    def __init__(
        self,
        model: Type[ModelType],
        model_name: str,
        to_model_fct: Callable,
        from_model_fct: Callable,
    ):
        self.model = model
        self.model_name = model_name
        self._to_model = to_model_fct  # type: ignore
        self._from_model = from_model_fct  # type: ignore
        self._table = _TaipyModel
        super().__init__()

    def load(self, model_id: str) -> Entity:
        entry = self.session.query(self._table).filter_by(model_id=model_id).first()
        if entry is None:
            raise ModelNotFound(self.model, model_id)  # type: ignore
        return self.__to_entity(entry)

    def _load_all(self, version_number: Optional[str] = None) -> List[Entity]:
        try:
            query = self.session.query(self._table).filter_by(model_name=self.model_name)
            query = self.__filter_by_version(query, version_number)
            return [self.__to_entity(e) for e in query.all()]
        except NoResultFound:
            return []

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[Entity]:
        try:
            query = (
                self.session.query(self._table)
                .filter_by(model_name=self.model_name)
                .filter(self._table.document.contains(by))
            )
            query = self.__filter_by_version(query, version_number)
            return [self.__to_entity(e) for e in query.all()]
        except NoResultFound:
            return []

    def _save(self, entity: Entity):
        model = self._to_model(entity)
        entry = self.session.query(self._table).filter_by(model_id=model.id).first()
        if entry:
            self.__update_entry(entry, model)
            return
        self.__insert_model(model)

    def _delete(self, model_id: str):
        number_of_deleted_entries = self.session.query(self._table).filter_by(model_id=model_id).delete()
        if not number_of_deleted_entries:
            raise ModelNotFound(str(self.model.__name__), model_id)
        self.session.commit()

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        entries = self._search(attribute, value, version_number)
        if entries:
            self._delete_many([e.id for e in entries])  # type: ignore

    def _delete_all(self):
        self.session.query(self._table).filter_by(model_name=self.model_name).delete()
        self.session.commit()

    def _delete_many(self, ids: Iterable[str]):
        self.session.execute(delete(self._table).where(self._table.model_id.in_(ids)))
        self.session.commit()

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[Entity]:
        query = (
            self.session.query(self._table)
            .filter_by(model_name=self.model_name)
            .filter(self._table.document.contains(f'"{attribute}": "{value}"'))
        )
        query = self.__filter_by_version(query, version_number)
        entry = query.first()
        if not entry:
            return None
        return self.__to_entity(entry)

    def _get_by_config_and_owner_id(self, config_id: str, owner_id: Optional[str]) -> Optional[Entity]:
        entity = self.__get_entities_by_config_and_owner(config_id, owner_id)
        return self.__to_entity(entity)

    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        res = {}
        configs_and_owner_ids = set(configs_and_owner_ids)

        for config, owner in configs_and_owner_ids:
            entry = self.__get_entities_by_config_and_owner(config.id, owner)
            if entry:
                entity = self.__to_entity(entry)
                key = config, owner
                res[key] = entity

        return res

    def __get_entities_by_config_and_owner(
        self, config_id: str, owner_id: Optional[str] = "", version_number: Optional[str] = None
    ) -> _TaipyModel:
        if owner_id:
            query = (
                self.session.query(self._table)
                .filter_by(model_name=self.model_name)
                .filter(self._table.document.contains(f'"config_id": "{config_id}"'))
                .filter(self._table.document.contains(f'"owner_id": "{owner_id}"'))
            )
        else:
            query = (
                self.session.query(self._table)
                .filter_by(model_name=self.model_name)
                .filter(self._table.document.contains(f'"config_id": "{config_id}"'))
                .filter(self._table.document.contains('"owner_id": null'))
            )
        query = self.__filter_by_version(query, version_number)
        return query.first()

    def __insert_model(self, model: ModelType):
        entry = self._table(
            model_id=model.id,  # type: ignore
            model_name=self.model_name,
            document=json.dumps(
                model.to_dict(),  # type: ignore
                ensure_ascii=False,
                indent=0,
                cls=_CustomEncoder,
                check_circular=False,
            ),
        )
        self.session.add(entry)
        self.session.commit()

    def __update_entry(self, entry, model):
        entry.document = json.dumps(
            model.to_dict(),
            ensure_ascii=False,
            indent=0,
            cls=_CustomEncoder,
            check_circular=False,
        )
        self.session.commit()

    def __to_entity(self, entry: _TaipyModel) -> Entity:
        return self.__model_to_entity(entry.document) if entry else None

    def __filter_by_version(self, query, version_number):
        from .._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        if version_number:
            query = query.filter(self._table.document.contains(f'"version": "{version_number}"'))
        return query

    def __model_to_entity(self, file_content):
        data = json.loads(file_content, cls=_CustomDecoder)
        model = self.model.from_dict(data)  # type: ignore
        entity = self._from_model(model)
        # Add version attribute on old entities. Used to migrate from <=2.0 to >=2.1 version.
        # To be removed on later versions
        if not data.get("version") and hasattr(entity, "version"):
            self._save(entity)
            from taipy.logger._taipy_logger import _TaipyLogger

            _TaipyLogger._get_logger().warning(
                f"Entity {entity.id} has automatically been assigned to version named " f"{entity.version}"
            )
        return entity

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        if isinstance(folder_path, str):
            folder: pathlib.Path = pathlib.Path(folder_path)
        else:
            folder = folder_path

        export_dir = folder / self.model_name
        if not export_dir.exists():
            export_dir.mkdir(parents=True)

        export_path = export_dir / f"{entity_id}.json"

        entry = self.session.query(self._table).filter_by(model_id=entity_id).first()
        if entry is None:
            raise ModelNotFound(self.model, entity_id)  # type: ignore

        with open(export_path, "w", encoding="utf-8") as export_file:
            export_file.write(entry.document)


class _TaipyVersionTable(_BaseSQLRepository[ModelType, Entity]):
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

    def __init__(
        self,
        model: Type[ModelType],
        to_model_fct: Callable,
        from_model_fct: Callable,
    ):
        self.model = model
        self._to_model = to_model_fct  # type: ignore
        self._from_model = from_model_fct  # type: ignore
        self._table = _TaipyVersion
        super().__init__()

    def load(self, id: str) -> Entity:
        entry = self.__get_by_id(id)
        if entry is None:
            raise ModelNotFound(self.model, id)  # type: ignore
        return self.__to_entity(entry)

    def _load_all(self, version_number: Optional[str] = None) -> List[Entity]:
        try:
            entries = self.session.query(self._table).all()
            return [self.__to_entity(e) for e in entries]
        except NoResultFound:
            return []

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[Entity]:
        try:
            entries = self.session.query(self._table).filter(self._table.config.contains(by)).all()
            return [self.__to_entity(e) for e in entries]
        except NoResultFound:
            return []

    def _save(self, entity: Entity):
        model = self._to_model(entity)
        entry = self.session.query(self._table).filter_by(id=model.id).first()
        if entry:
            self.__update_entry(entry, model)
            return
        self.__insert_model(model)

    def _delete(self, id: str):
        number_of_deleted_entries = self.session.query(self._table).filter_by(id=id).delete()
        if not number_of_deleted_entries:
            raise ModelNotFound(str(self.model.__name__), id)
        self.session.commit()

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        entries = self._search(attribute, value, version_number)
        self._delete_many([e.id for e in entries])  # type: ignore

    def _delete_all(self):
        self.session.query(self._table).delete()
        self.session.commit()

    def _delete_many(self, ids: Iterable[str]):
        self.session.execute(delete(self._table).where(self._table.id.in_(ids)))
        self.session.commit()

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[Entity]:
        entry = (
            self.session.query(self._table).filter(self._table.config.contains(f'"{attribute}": "{value}"'))
        ).first()
        if not entry:
            return None
        return self.__to_entity(entry)

    def __insert_model(self, model: ModelType):
        entry = self._table(id=model.id, config=model.config, creation_date=model.creation_date)  # type: ignore
        self.session.add(entry)
        self.session.commit()

    def __update_entry(self, entry, model):
        entry.config = Config._to_json(model.config)
        self.session.commit()

    def __to_entity(self, entry: _TaipyVersion) -> Entity:
        return self._from_model(entry)
        # return self.__model_to_entity(entry.config) if entry else None

    def __model_to_entity(self, file_content):
        data = json.loads(file_content, cls=_CustomDecoder)
        model = self.model.from_dict(data)  # type: ignore
        entity = self._from_model(model)
        # Add version attribute on old entities. Used to migrate from <=2.0 to >=2.1 version.
        # To be removed on later versions
        if not data.get("version") and hasattr(entity, "version"):
            self._save(entity)
            from taipy.logger._taipy_logger import _TaipyLogger

            _TaipyLogger._get_logger().warning(
                f"Entity {entity.id} has automatically been assigned to version named " f"{entity.version}"
            )
        return entity

    def __get_by_id(self, id):
        return self.session.query(self._table).filter_by(id=id).first()

    def _set_latest_version(self, version_number):
        if old_latest := self.session.query(self._table).filter_by(is_latest=True).first():
            old_latest.is_latest = False

        version = self.__get_by_id(version_number)
        version.is_latest = True

        self.session.commit()

    def _get_latest_version(self):
        if latest := self.session.query(self._table).filter_by(is_latest=True).first():
            return latest.id
        return ""

    def _set_development_version(self, version_number):
        if old_development := self.session.query(self._table).filter_by(is_development=True).first():
            old_development.is_development = False

        version = self.__get_by_id(version_number)
        version.is_development = True

        self._set_latest_version(version_number)

        self.session.commit()

    def _get_development_version(self):
        if development := self.session.query(self._table).filter_by(is_development=True).first():
            return development.id
        raise ModelNotFound

    def _set_production_version(self, version_number):
        version = self.__get_by_id(version_number)
        version.is_production = True

        self._set_latest_version(version_number)

        self.session.commit()

    def _get_production_version(self):
        if productions := self.session.query(self._table).filter_by(is_production=True).all():
            return [p.id for p in productions]
        return []

    def _delete_production_version(self, version_number):
        version = self.__get_by_id(version_number)

        if not version or not version.is_production:
            raise VersionIsNotProductionVersion(f"Version {version_number} is not a production version.")
        version.is_production = False

        self.session.commit()


class _SQLRepository(_BaseSQLRepository):
    def __init__(
        self,
        model: Type[ModelType],
        model_name: str,
        to_model_fct: Callable,
        from_model_fct: Callable,
    ):
        self._table: _BaseSQLRepository = (
            _TaipyVersionTable(model, to_model_fct, from_model_fct)  # type: ignore
            if model_name == "version"
            else _TaipyModelTable(model, model_name, to_model_fct, from_model_fct)  # type: ignore
        )
        super().__init__()

    def load(self, model_id: str) -> Entity:  # type: ignore
        return self._table.load(model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[Entity]:
        return self._table._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[Entity]:
        return self._table._load_all_by(by, version_number)

    def _save(self, entity: Entity):
        self._table._save(entity)

    def _delete(self, model_id: str):
        self._table._delete(model_id)

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        self._table._delete_by(attribute, value, version_number)  # type: ignore

    def _delete_all(self):
        self._table._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        self._table._delete_many(ids)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[Entity]:
        return self._table._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        self._table._export(entity_id, folder_path)

    def _get_by_config_and_owner_id(self, config_id: str, owner_id: Optional[str]) -> Optional[Entity]:
        return self._table._get_by_config_and_owner_id(config_id, owner_id)  # type: ignore

    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids):
        return self._table._get_by_configs_and_owner_ids(configs_and_owner_ids)

    def _set_latest_version(self, version_number):
        self._table._set_latest_version(version_number)

    def _get_latest_version(self):
        return self._table._get_latest_version()

    def _set_development_version(self, version_number):
        self._table._set_development_version(version_number)

    def _get_development_version(self):
        return self._table._get_development_version()

    def _set_production_version(self, version_number):
        self._table._set_production_version(version_number)

    def _get_production_version(self):
        return self._table._get_production_version()

    def _delete_production_version(self, version_number):
        self._table._delete_production_version(version_number)
