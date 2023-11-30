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

from datetime import datetime

from .._repository._abstract_converter import _AbstractConverter
from ..cycle._cycle_model import _CycleModel
from ..cycle.cycle import Cycle


class _CycleConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, cycle: Cycle) -> _CycleModel:
        return _CycleModel(
            id=cycle.id,
            name=cycle._name,
            frequency=cycle._frequency,
            creation_date=cycle._creation_date.isoformat(),
            start_date=cycle._start_date.isoformat(),
            end_date=cycle._end_date.isoformat(),
            properties=cycle._properties.data,
        )

    @classmethod
    def _model_to_entity(cls, model: _CycleModel) -> Cycle:
        return Cycle(
            id=model.id,
            name=model.name,
            frequency=model.frequency,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            start_date=datetime.fromisoformat(model.start_date),
            end_date=datetime.fromisoformat(model.end_date),
        )
