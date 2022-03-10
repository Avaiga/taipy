from datetime import timedelta

from taipy.core.common.frequency import Frequency
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.cycle.cycle import Cycle


def test_create_cycle_entity(current_datetime):
    cycle_1 = Cycle(
        Frequency.DAILY,
        {"key": "value"},
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
        name="foo",
    )
    assert cycle_1.id is not None
    assert cycle_1.name == "foo"
    assert cycle_1.properties == {"key": "value"}
    assert cycle_1.creation_date == current_datetime
    assert cycle_1.start_date == current_datetime
    assert cycle_1.end_date == current_datetime
    assert cycle_1.key == "value"
    assert cycle_1.frequency == Frequency.DAILY

    cycle_2 = Cycle(Frequency.YEARLY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_2.name.startswith(str(Frequency.YEARLY))
    assert cycle_2.frequency == Frequency.YEARLY

    cycle_3 = Cycle(Frequency.MONTHLY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_3.name.startswith(str(Frequency.MONTHLY))
    assert cycle_3.frequency == Frequency.MONTHLY

    cycle_4 = Cycle(Frequency.WEEKLY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_4.name.startswith(str(Frequency.WEEKLY))
    assert cycle_4.frequency == Frequency.WEEKLY

    cycle_5 = Cycle(Frequency.DAILY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_5.name.startswith(str(Frequency.DAILY))
    assert cycle_5.frequency == Frequency.DAILY


def test_add_property_to_scenario(current_datetime):
    cycle = Cycle(
        Frequency.WEEKLY,
        {"key": "value"},
        current_datetime,
        current_datetime,
        current_datetime,
        name="foo",
    )
    assert cycle.properties == {"key": "value"}
    assert cycle.key == "value"

    cycle.properties["new_key"] = "new_value"

    assert cycle.properties == {"key": "value", "new_key": "new_value"}
    assert cycle.key == "value"
    assert cycle.new_key == "new_value"


def test_auto_set_and_reload(current_datetime):
    cycle_1 = Cycle(
        Frequency.WEEKLY,
        {"key": "value"},
        current_datetime,
        current_datetime,
        current_datetime,
        name="foo",
    )

    _CycleManager._set(cycle_1)
    cycle_2 = _CycleManager._get(cycle_1)

    assert cycle_1.frequency == Frequency.WEEKLY
    cycle_1.frequency = Frequency.MONTHLY
    assert cycle_1.frequency == Frequency.MONTHLY
    assert cycle_2.frequency == Frequency.MONTHLY

    new_datetime = current_datetime + timedelta(1)

    assert cycle_1.creation_date == current_datetime
    cycle_1.creation_date = new_datetime
    assert cycle_1.creation_date == new_datetime
    assert cycle_2.creation_date == new_datetime

    assert cycle_1.start_date == current_datetime
    cycle_1.start_date = new_datetime
    assert cycle_1.start_date == new_datetime
    assert cycle_2.start_date == new_datetime

    assert cycle_1.end_date == current_datetime
    cycle_1.end_date = new_datetime
    assert cycle_1.end_date == new_datetime
    assert cycle_2.end_date == new_datetime

    assert cycle_1.name == "foo"
    cycle_1.name = "def"
    assert cycle_1.name == "def"
    assert cycle_2.name == "def"

    assert cycle_1.properties == {"key": "value"}
    cycle_1._properties["qux"] = 5
    assert cycle_1.properties["qux"] == 5
    assert cycle_2.properties["qux"] == 5

    with cycle_1 as cycle:
        assert cycle.frequency == Frequency.MONTHLY
        assert cycle.creation_date == new_datetime
        assert cycle.start_date == new_datetime
        assert cycle.end_date == new_datetime
        assert cycle.name == "def"
        assert cycle._is_in_context

        new_datetime_2 = new_datetime + timedelta(1)
        cycle.frequency = Frequency.YEARLY
        cycle.creation_date = new_datetime_2
        cycle.start_date = new_datetime_2
        cycle.end_date = new_datetime_2
        cycle.name = "abc"
        assert cycle.name == "def"
        assert cycle._name == "abc"

    assert cycle.frequency == Frequency.YEARLY
    assert cycle.creation_date == new_datetime_2
    assert cycle.start_date == new_datetime_2
    assert cycle.end_date == new_datetime_2
    assert cycle.name == "abc"
