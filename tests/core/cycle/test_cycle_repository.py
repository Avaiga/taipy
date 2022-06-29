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

from datetime import datetime

from taipy.config.scenario.frequency import Frequency

from src.taipy.core.cycle._cycle_repository import _CycleRepository
from src.taipy.core.cycle.cycle import Cycle


def test_save_and_load(tmpdir, cycle):
    repository = _CycleRepository()
    repository.base_path = tmpdir
    repository._save(cycle)
    cc = repository.load(cycle.id)

    assert isinstance(cc, Cycle)
    assert cc.id == cycle.id
    assert cc.name == cycle.name
    assert cc.creation_date == cycle.creation_date


def test_from_and_to_model(cycle, cycle_model):
    repository = _CycleRepository()
    assert repository._to_model(cycle) == cycle_model
    assert repository._from_model(cycle_model) == cycle


def test_get_primary(tmpdir, cycle, current_datetime):

    cycle_repository = _CycleRepository()
    cycle_repository.base_path = tmpdir

    assert len(cycle_repository._load_all()) == 0

    cycle_repository._save(cycle)
    cycle_1 = cycle_repository.load(cycle.id)
    cycle_2 = Cycle(Frequency.MONTHLY, {}, current_datetime, current_datetime, current_datetime, name="foo")
    cycle_repository._save(cycle_2)
    cycle_2 = cycle_repository.load(cycle_2.id)

    assert len(cycle_repository._load_all()) == 2
    assert len(cycle_repository.get_cycles_by_frequency_and_start_date(cycle_1.frequency, cycle_1.start_date)) == 1
    assert len(cycle_repository.get_cycles_by_frequency_and_start_date(cycle_2.frequency, cycle_2.start_date)) == 1
    assert (
        len(cycle_repository.get_cycles_by_frequency_and_start_date(Frequency.WEEKLY, datetime(2000, 1, 1, 1, 0, 0, 0)))
        == 0
    )

    assert (
        len(cycle_repository.get_cycles_by_frequency_and_overlapping_date(cycle_1.frequency, cycle_1.creation_date))
        == 1
    )
    assert (
        cycle_repository.get_cycles_by_frequency_and_overlapping_date(cycle_1.frequency, cycle_1.creation_date)[0]
        == cycle_1
    )
    assert (
        len(
            cycle_repository.get_cycles_by_frequency_and_overlapping_date(
                Frequency.WEEKLY, datetime(2000, 1, 1, 1, 0, 0, 0)
            )
        )
        == 0
    )
