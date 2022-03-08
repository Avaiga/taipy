from datetime import datetime

from taipy.core.common.frequency import Frequency
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_repository import CycleRepository


def test_save_and_load(tmpdir, cycle):
    repository = CycleRepository()
    repository.base_path = tmpdir
    repository.save(cycle)
    cc = repository.load(cycle.id)

    assert isinstance(cc, Cycle)
    assert cc.id == cycle.id
    assert cc.name == cycle.name
    assert cc.creation_date == cycle.creation_date


def test_from_and_to_model(cycle, cycle_model):
    repository = CycleRepository()
    assert repository.to_model(cycle) == cycle_model
    assert repository.from_model(cycle_model) == cycle


def test_get_masters(tmpdir, cycle, current_datetime):

    cycle_repository = CycleRepository()
    cycle_repository.base_path = tmpdir

    assert len(cycle_repository.load_all()) == 0

    cycle_repository.save(cycle)
    cycle_1 = cycle_repository.load(cycle.id)
    cycle_2 = Cycle(Frequency.MONTHLY, {}, current_datetime, current_datetime, current_datetime, name="foo")
    cycle_repository.save(cycle_2)
    cycle_2 = cycle_repository.load(cycle_2.id)

    assert len(cycle_repository.load_all()) == 2
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
