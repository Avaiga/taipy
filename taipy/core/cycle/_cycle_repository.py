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

import pathlib
from datetime import datetime
from typing import Callable, List

from taipy.core._repository import _FileSystemRepository
from taipy.core.common.frequency import Frequency
from taipy.core.config.config import Config
from taipy.core.cycle._cycle_model import _CycleModel
from taipy.core.cycle.cycle import Cycle


class _CycleRepository(_FileSystemRepository[_CycleModel, Cycle]):
    def __init__(self):
        super().__init__(model=_CycleModel, dir_name="cycles")

    def _to_model(self, cycle: Cycle) -> _CycleModel:
        return _CycleModel(
            id=cycle.id,
            name=cycle._name,
            frequency=cycle._frequency,
            creation_date=cycle._creation_date.isoformat(),
            start_date=cycle._start_date.isoformat(),
            end_date=cycle._end_date.isoformat(),
            properties=cycle._properties.data,
        )

    def _from_model(self, model: _CycleModel) -> Cycle:
        return Cycle(
            id=model.id,
            name=model.name,
            frequency=model.frequency,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            start_date=datetime.fromisoformat(model.start_date),
            end_date=datetime.fromisoformat(model.end_date),
        )

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    def get_cycles_by_frequency_and_start_date(self, frequency: Frequency, start_date: datetime) -> List[Cycle]:
        return self.__get_cycles_cdt(lambda cycle: cycle.frequency == frequency and cycle.start_date == start_date)

    def get_cycles_by_frequency_and_overlapping_date(self, frequency: Frequency, date: datetime) -> List[Cycle]:
        return self.__get_cycles_cdt(
            lambda cycle: cycle.frequency == frequency and cycle.start_date <= date <= cycle.end_date
        )

    def __get_cycles_cdt(self, cdt: Callable[[Cycle], bool]) -> List[Cycle]:
        return [cycle for cycle in self._load_all() if cdt(cycle)]
