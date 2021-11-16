from datetime import datetime

import pytest

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.exceptions.cycle import NonExistingCycle


def test_save_and_get_cycle_entity(tmpdir, cycle):
    cycle_manager = CycleManager()
    cycle_manager.repository.base_path = tmpdir

    assert len(cycle_manager.get_all()) == 0

    cycle_manager.set(cycle)

    cycle_1 = cycle_manager.get(cycle.id)

    assert cycle_1.id == cycle.id
    assert cycle_1.name == cycle.name
    assert cycle_1.properties == cycle.properties
    assert cycle_1.creation_date == cycle.creation_date
    assert cycle_1.start_date == cycle.start_date
    assert cycle_1.end_date == cycle.end_date
    assert cycle_1.frequency == cycle.frequency

    assert len(cycle_manager.get_all()) == 1
    assert cycle_manager.get(cycle.id) == cycle
    assert cycle_manager.get(cycle.id).name == cycle.name
    assert isinstance(cycle_manager.get(cycle.id).creation_date, datetime)
    assert cycle_manager.get(cycle.id).creation_date == cycle.creation_date
    assert cycle_manager.get(cycle.id).frequency == Frequency.DAILY

    cycle_2_id = CycleId("cycle_2")
    with pytest.raises(NonExistingCycle):
        assert cycle_manager.get(cycle_2_id)

    cycle_3 = Cycle(
        Frequency.MONTHLY,
        {},
        name="   bar/ξéà   ",
    )
    cycle_manager.set(cycle_3)

    cycle_3_entity = cycle_manager.get(cycle_3.id)

    assert len(cycle_manager.get_all()) == 2
    assert cycle_3_entity.id == cycle_3.id
    assert cycle_3_entity.name == cycle_3.name
    assert cycle_3_entity.properties == cycle_3.properties
    assert isinstance(cycle_3_entity.creation_date, datetime)
    assert cycle_3_entity.start_date is not None
    assert cycle_3_entity.end_date is not None
    assert cycle_3_entity.frequency == cycle_3.frequency

    assert len(cycle_manager.get_cycles_by_frequency_and_creation_date(cycle_1.frequency, cycle_1.creation_date)) == 1
    assert len(cycle_manager.get_cycles_by_frequency_and_creation_date(cycle_3.frequency, cycle_3.creation_date)) == 1
    assert (
        len(cycle_manager.get_cycles_by_frequency_and_creation_date(Frequency.WEEKLY, datetime(2000, 1, 1, 1, 0, 0, 0)))
        == 0
    )

    assert (
        len(cycle_manager.get_cycles_by_frequency_and_overlapping_date(cycle_1.frequency, cycle_1.creation_date)) == 1
    )
    assert (
        cycle_manager.get_cycles_by_frequency_and_overlapping_date(cycle_1.frequency, cycle_1.creation_date)[0]
        == cycle_1
    )
    assert (
        len(
            cycle_manager.get_cycles_by_frequency_and_overlapping_date(
                Frequency.WEEKLY, datetime(2000, 1, 1, 1, 0, 0, 0)
            )
        )
        == 0
    )


def test_create_and_delete_cycle_entity(tmpdir):
    cycle_manager = CycleManager()
    cycle_manager.repository.base_path = tmpdir

    assert len(cycle_manager.get_all()) == 0

    cycle_1 = cycle_manager.create(Frequency.DAILY, name="fOo   ", key="value")

    assert cycle_1.id is not None
    assert cycle_1.name == "foo"
    assert cycle_1.properties == {"key": "value"}
    assert cycle_1.creation_date is not None
    assert cycle_1.start_date is not None
    assert cycle_1.end_date is not None
    assert cycle_1.key == "value"
    assert cycle_1.frequency == Frequency.DAILY

    cycle_1_id = cycle_1.id

    assert len(cycle_manager.get_all()) == 1
    assert cycle_manager.get(cycle_1_id) == cycle_1
    assert cycle_manager.get(cycle_1_id).name == "foo"
    assert isinstance(cycle_manager.get(cycle_1_id).creation_date, datetime)
    assert cycle_manager.get(cycle_1_id).frequency == Frequency.DAILY

    cycle_2_id = CycleId("cycle_2")
    with pytest.raises(NonExistingCycle):
        assert cycle_manager.get(cycle_2_id)

    cycle_3 = cycle_manager.create(Frequency.MONTHLY, "   bar/ξéà   ")

    assert cycle_3.id is not None
    assert cycle_3.name == "bar-xea"
    assert cycle_3.properties == {}
    assert isinstance(cycle_3.creation_date, datetime)
    assert cycle_3.frequency == Frequency.MONTHLY

    cycle_3_id = cycle_3.id

    assert len(cycle_manager.get_all()) == 2
    assert cycle_manager.get(cycle_3_id).name == "bar-xea"
    assert cycle_manager.get(cycle_3_id).properties == {}

    cycle_4 = cycle_manager.create(Frequency.YEARLY, "ξéà   ")
    cycle_4_id = cycle_4.id

    assert len(cycle_manager.get_all()) == 3

    cycle_manager.delete(cycle_4_id)

    assert len(cycle_manager.get_all()) == 2
    with pytest.raises(NonExistingCycle):
        cycle_manager.get(cycle_4_id)

    cycle_manager.delete_all()
    assert len(cycle_manager.get_all()) == 0
