from datetime import datetime

import pytest

from taipy.common.alias import CycleId
from taipy.common.frequency import Frequency
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.exceptions.cycle import NonExistingCycle


def test_save_and_get_cycle_entity(tmpdir, cycle, current_datetime):
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
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
        name="   bar/ξéà   ",
        id=cycle_1.id,
    )
    cycle_manager.set(cycle_3)

    cycle_3 = cycle_manager.get(cycle_1.id)

    assert len(cycle_manager.get_all()) == 1
    assert cycle_3.id == cycle_1.id
    assert cycle_3.name == cycle_3.name
    assert cycle_3.properties == cycle_3.properties
    assert cycle_3.creation_date == current_datetime
    assert cycle_3.start_date == current_datetime
    assert cycle_3.end_date == current_datetime
    assert cycle_3.frequency == cycle_3.frequency


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
    assert cycle_1.start_date < cycle_1.creation_date < cycle_1.end_date
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


def test_get_cycle_start_date_and_end_date():
    creation_date_1 = datetime.fromisoformat("2021-11-11T11:11:01.000001")

    daily_start_date_1 = CycleManager.get_start_date_of_cycle(Frequency.DAILY, creation_date=creation_date_1)
    weekly_start_date_1 = CycleManager.get_start_date_of_cycle(Frequency.WEEKLY, creation_date=creation_date_1)
    monthly_start_date_1 = CycleManager.get_start_date_of_cycle(Frequency.MONTHLY, creation_date=creation_date_1)
    yearly_start_date_1 = CycleManager.get_start_date_of_cycle(Frequency.YEARLY, creation_date=creation_date_1)

    assert daily_start_date_1 == datetime.fromisoformat("2021-11-11T00:00:00.000000")
    assert weekly_start_date_1 == datetime.fromisoformat("2021-11-08T00:00:00.000000")
    assert monthly_start_date_1 == datetime.fromisoformat("2021-11-01T00:00:00.000000")
    assert yearly_start_date_1 == datetime.fromisoformat("2021-01-01T00:00:00.000000")

    daily_end_date_1 = CycleManager.get_end_date_of_cycle(Frequency.DAILY, start_date=daily_start_date_1)
    weekly_end_date_1 = CycleManager.get_end_date_of_cycle(Frequency.WEEKLY, start_date=weekly_start_date_1)
    monthly_end_date_1 = CycleManager.get_end_date_of_cycle(Frequency.MONTHLY, start_date=monthly_start_date_1)
    yearly_end_date_1 = CycleManager.get_end_date_of_cycle(Frequency.YEARLY, start_date=yearly_start_date_1)

    assert daily_end_date_1 == datetime.fromisoformat("2021-11-11T23:59:59.999999")
    assert weekly_end_date_1 == datetime.fromisoformat("2021-11-14T23:59:59.999999")
    assert monthly_end_date_1 == datetime.fromisoformat("2021-11-30T23:59:59.999999")
    assert yearly_end_date_1 == datetime.fromisoformat("2021-12-31T23:59:59.999999")

    creation_date_2 = datetime.now()

    daily_start_date_2 = CycleManager.get_start_date_of_cycle(Frequency.DAILY, creation_date=creation_date_2)
    daily_end_date_2 = CycleManager.get_end_date_of_cycle(Frequency.DAILY, daily_start_date_2)
    assert daily_start_date_2.date() == creation_date_2.date()
    assert daily_end_date_2.date() == creation_date_2.date()
    assert daily_start_date_2 < creation_date_2 < daily_end_date_2

    weekly_start_date_2 = CycleManager.get_start_date_of_cycle(Frequency.WEEKLY, creation_date=creation_date_2)
    weekly_end_date_2 = CycleManager.get_end_date_of_cycle(Frequency.WEEKLY, weekly_start_date_2)
    assert weekly_start_date_2 < creation_date_2 < weekly_end_date_2

    monthly_start_date_2 = CycleManager.get_start_date_of_cycle(Frequency.MONTHLY, creation_date=creation_date_2)
    monthly_end_date_2 = CycleManager.get_end_date_of_cycle(Frequency.MONTHLY, monthly_start_date_2)
    assert monthly_start_date_2.month == creation_date_2.month and monthly_start_date_2.day == 1
    assert monthly_end_date_2.month == creation_date_2.month
    assert monthly_start_date_2 < creation_date_2 < monthly_end_date_2

    yearly_start_date_2 = CycleManager.get_start_date_of_cycle(Frequency.YEARLY, creation_date=creation_date_2)
    yearly_end_date_2 = CycleManager.get_end_date_of_cycle(Frequency.YEARLY, yearly_start_date_2)
    assert yearly_start_date_2.year == creation_date_2.year
    assert yearly_start_date_2 == datetime(creation_date_2.year, 1, 1)
    assert yearly_end_date_2.year == creation_date_2.year
    assert yearly_end_date_2.date() == datetime(creation_date_2.year, 12, 31).date()
    assert yearly_start_date_2 < creation_date_2 < yearly_end_date_2
