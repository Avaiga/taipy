from datetime import date

from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency


def test_create_cycle_entity(current_datetime, week_example):

    cycle_1 = Cycle(Frequency.DAILY, {"key": "value"}, name="   bAr/ξéà    ")
    assert cycle_1.id is not None
    assert cycle_1.name == "bar-xea"
    assert cycle_1.properties == {"key": "value"}
    assert cycle_1.creation_date is not None
    assert cycle_1.start_date.date() == cycle_1.creation_date.date()
    assert cycle_1.end_date.date() == cycle_1.creation_date.date()
    assert cycle_1.start_date <= cycle_1.creation_date <= cycle_1.end_date
    assert cycle_1.key == "value"
    assert cycle_1.frequency == Frequency.DAILY

    cycle_2 = Cycle(Frequency.YEARLY, {}, creation_date=current_datetime)

    assert cycle_2.name.startswith(str(Frequency.YEARLY))
    assert cycle_2.frequency == Frequency.YEARLY
    assert cycle_2.creation_date == current_datetime
    assert cycle_2.start_date.date() == date(current_datetime.year, 1, 1)
    assert cycle_2.end_date.date() == date(current_datetime.year, 12, 31)
    assert cycle_2.start_date.year == cycle_2.creation_date.year == cycle_2.end_date.year

    cycle_3 = Cycle(Frequency.WEEKLY, {}, creation_date=week_example)

    assert cycle_3.name.startswith(str(Frequency.WEEKLY))
    assert cycle_3.frequency == Frequency.WEEKLY
    assert cycle_3.creation_date == week_example
    assert cycle_3.start_date.date() == date(2021, 11, 15)
    assert cycle_3.end_date.date() == date(2021, 11, 21)

    cycle_4 = Cycle(
        Frequency.MONTHLY,
        {},
        creation_date=current_datetime,
    )

    assert cycle_4.name.startswith(str(Frequency.MONTHLY))
    assert cycle_4.frequency == Frequency.MONTHLY
    assert cycle_4.creation_date == current_datetime
    assert cycle_4.start_date.date() == date(current_datetime.year, current_datetime.month, 1)
    assert cycle_4.end_date.month == current_datetime.month

    cycle_5 = Cycle(
        Frequency.MONTHLY, {}, creation_date=current_datetime, start_date=current_datetime, end_date=current_datetime
    )
    assert cycle_5.creation_date == current_datetime
    assert cycle_5.start_date == current_datetime
    assert cycle_5.end_date == current_datetime


def test_add_property_to_scenario():
    cycle_1 = Cycle(Frequency.WEEKLY, {"key": "value"}, name="foo")
    assert cycle_1.properties == {"key": "value"}
    assert cycle_1.key == "value"

    cycle_1.properties["new_key"] = "new_value"

    assert cycle_1.properties == {"key": "value", "new_key": "new_value"}
    assert cycle_1.key == "value"
    assert cycle_1.new_key == "new_value"
