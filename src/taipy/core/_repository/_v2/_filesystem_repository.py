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
from typing import Any, Iterable, List, Optional, Type, Union

from src.taipy.core.common.typing import Entity, Json, ModelType
from taipy.config.config import Config

from ...exceptions import ModelNotFound
from ._repository import _AbstractRepository, _CustomDecoder, _CustomEncoder


class _FileSystemRepository(_AbstractRepository[ModelType, Entity]):
    """
    Holds common methods to be used and extended when the need for saving
    dataclasses as JSON files in local storage emerges.

    Some lines have type: ignore because MyPy won't recognize some generic attributes. This
    should be revised in the future.

    Attributes:
        model (ModelType): Generic dataclass.
        dir_name (str): Folder that will hold the files for this dataclass model.
    """

    def __init__(self, model: Type[ModelType], dir_name: str):
        self.model = model
        self._dir_name = dir_name

    @property
    def dir_path(self):
        return self._storage_folder / self._dir_name

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)

    def _save(self, entity: Entity):
        self.__create_directory_if_not_exists()

        # TODO: implement __from_entity on models
        model = self.model.__from_entity(entity)
        self._get_model_filepath(model.id).write_text(
            json.dumps(model.to_dict(), ensure_ascii=False, indent=0, cls=_CustomEncoder, check_circular=False)
        )

    def _get(self, filepath: pathlib.Path) -> Json:
        with pathlib.Path(filepath).open(encoding="UTF-8") as source:
            return json.load(source)

    def load(self, model_id: str) -> Entity:
        try:
            model = self.model(**self._get(self._get_model_filepath(model_id)))
            return model.__to_entity()
        except FileNotFoundError:
            raise ModelNotFound(str(self.dir_path), model_id)

    def _load_all(self, version_number: Optional[str]) -> List[Entity]:
        """
        Load all entities from a specific version.
        """
        from ..._version._version_manager_factory import _VersionManagerFactory

        version_number = _VersionManagerFactory._build_manager()._replace_version_number(version_number)

        r = []
        return r

    def _load_all_by(self, by, version_number: Optional[str]) -> List[Entity]:
        pass

    def _delete(self, entity_id: str):
        pass

    def _delete_all(self):
        pass

    def _delete_many(self, ids: Iterable[str]):
        pass

    def _search(self, attribute: str, value: Any, version_number: Optional[str]) -> Optional[Entity]:
        pass

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        pass

    def __create_directory_if_not_exists(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def _get_model_filepath(self, model_id) -> pathlib.Path:
        return self.dir_path / f"{model_id}.json"
