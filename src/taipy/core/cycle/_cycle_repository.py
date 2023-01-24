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

import pathlib
from datetime import datetime
from typing import Any, Callable, Iterable, List, Optional, Union

from taipy.config.common.frequency import Frequency

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ..cycle._cycle_model import _CycleModel
from ..cycle.cycle import Cycle


class _CycleRepository(_AbstractRepository[_CycleModel, Cycle]):  # type: ignore
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

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

    def load(self, model_id: str) -> Cycle:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = "all") -> List[Cycle]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = "all") -> List[Cycle]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: Cycle):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = "all") -> Optional[Cycle]:
        return self.repo._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(entity_id, folder_path)

    def get_cycles_by_frequency_and_start_date(self, frequency: Frequency, start_date: datetime) -> List[Cycle]:
        return self.__get_cycles_cdt(lambda cycle: cycle.frequency == frequency and cycle.start_date == start_date)

    def get_cycles_by_frequency_and_overlapping_date(self, frequency: Frequency, date: datetime) -> List[Cycle]:
        return self.__get_cycles_cdt(
            lambda cycle: cycle.frequency == frequency and cycle.start_date <= date <= cycle.end_date
        )

    def __get_cycles_cdt(self, cdt: Callable[[Cycle], bool]) -> List[Cycle]:
        return [cycle for cycle in self._load_all() if cdt(cycle)]
