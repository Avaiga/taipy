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

import json
import pathlib
from abc import abstractmethod
from typing import Any, Callable, Iterable, List, Optional, Type, TypeVar, Union

from sqlalchemy import create_engine, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from taipy.config.config import Config

from ..exceptions.exceptions import MissingRequiredProperty, ModelNotFound
from ._repository import _AbstractRepository, _CustomDecoder, _CustomEncoder
from ._sql_model import Base, _TaipyModel

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")


class _SQLRepository(_AbstractRepository[ModelType, Entity]):
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
        properties = Config.global_config.repository_properties
        self.model = model
        self.model_name = model_name
        self._to_model = to_model_fct  # type: ignore
        self._from_model = from_model_fct  # type: ignore

        try:
            # More sql databases can be easily added in the future
            self.engine = create_engine(f"sqlite:///{properties.get('db_location')}")

            # Maybe this should be in the taipy package? So it's not executed every time
            # the class is instantiated
            Base.metadata.create_all(self.engine)
            _session = sessionmaker(bind=self.engine)
            self.session = _session()

        except KeyError:
            raise MissingRequiredProperty("Missing property db_location")

    def load(self, model_id: str) -> Entity:
        entry = self.session.query(_TaipyModel).filter_by(model_id=model_id).first()
        if entry is None:
            raise ModelNotFound(self.model, model_id)  # type: ignore
        return self.__to_entity(entry)

    def _load_all(self) -> List[Entity]:
        try:
            entries = self.session.query(_TaipyModel).filter_by(model_name=self.model_name)
            return [self.__to_entity(e) for e in entries]
        except NoResultFound:
            return []

    def _load_all_by(self, by) -> List[Entity]:
        try:
            entries = (
                self.session.query(_TaipyModel)
                .filter_by(model_name=self.model_name)
                .filter(_TaipyModel.document.contains(by))
            )
            return [self.__to_entity(e) for e in entries]
        except NoResultFound:
            return []

    def _save(self, entity: Entity):
        model = self._to_model(entity)
        entry = self.session.query(_TaipyModel).filter_by(model_id=model.id).first()
        if entry:
            self.__update_entry(entry, model)
            return
        self.__insert_model(model)

    def _delete(self, model_id: str):
        self.session.query(_TaipyModel).filter_by(model_id=model_id).delete()
        self.session.commit()

    def _delete_all(self):
        self.session.query(_TaipyModel).filter_by(model_name=self.model_name).delete()
        self.session.commit()

    def _delete_many(self, ids: Iterable[str]):
        self.session.execute(delete(_TaipyModel).where(_TaipyModel.model_id.in_(ids)))
        self.session.commit()

    def _search(self, attribute: str, value: Any) -> Optional[Entity]:
        entry = (
            self.session.query(_TaipyModel)
            .filter_by(model_name=self.model_name)
            .filter(_TaipyModel.document.contains(f'"{attribute}": "{value}"'))
        ).first()
        if not entry:
            return None
        return self.__to_entity(entry)

    def _get_by_config_and_parent_id(self, config_id: str, parent_id: Optional[str]) -> Optional[Entity]:
        entities = iter(self.__get_entities_by_config_and_parent(config_id, parent_id))
        return next(entities, None)

    def _get_by_configs_and_parent_ids(self, configs_and_parent_ids):
        # Design in order to optimize performance on Entity creation.
        # Maintainability and readability were impacted.
        res = {}
        configs_and_parent_ids = set(configs_and_parent_ids)

        for config, parent in configs_and_parent_ids:
            entry = self.__get_entities_by_config_and_parent(config, parent, only_first=True)
            if entry:
                entity = self.__to_entity(entry)
                key = config, parent
                res[key] = entity
                configs_and_parent_ids.remove(key)

        return res

    def __get_entities_by_config_and_parent(
        self, config_id: str, parent_id: Optional[str] = "", only_first: bool = False
    ):
        query = (
            self.session.query(_TaipyModel)
            .filter_by(model_name=self.model_name)
            .filter(_TaipyModel.document.contains(f'"config_id": "{config_id}"'))
            .filter(_TaipyModel.document.contains(f'"parent_id": "{parent_id}"'))
        )
        if only_first:
            return query.first()
        return query.all()

    def __insert_model(self, model: ModelType):
        entry = _TaipyModel(
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
        return self.__model_to_entity(entry.document)

    def __model_to_entity(self, file_content):
        data = json.loads(file_content, cls=_CustomDecoder)
        model = self.model.from_dict(data)  # type: ignore
        return self._from_model(model)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        if isinstance(folder_path, str):
            folder: pathlib.Path = pathlib.Path(folder_path)
        else:
            folder = folder_path

        export_dir = folder / self.model_name
        if not export_dir.exists():
            export_dir.mkdir(parents=True)

        export_path = export_dir / f"{entity_id}.json"

        entry = self.session.query(_TaipyModel).filter_by(model_id=entity_id).first()
        if entry is None:
            raise ModelNotFound(self.model, entity_id)  # type: ignore

        with open(export_path, "w", encoding="utf-8") as export_file:
            export_file.write(entry.document)
