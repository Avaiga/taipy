# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import datetime

from taipy.common.config import Config

from .._repository._abstract_converter import _AbstractConverter
from .._version._version import _Version
from .._version._version_model import _VersionModel


class _VersionConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, version: _Version) -> _VersionModel:
        return _VersionModel(
            id=version.id, config=Config._to_json(version.config), creation_date=version.creation_date.isoformat()
        )  # type: ignore[attr-defined]

    @classmethod
    def _model_to_entity(cls, model: _VersionModel) -> _Version:
        version = _Version(id=model.id, config=Config._from_json(model.config))  # type: ignore[attr-defined]
        version.creation_date = datetime.fromisoformat(model.creation_date)
        return version
