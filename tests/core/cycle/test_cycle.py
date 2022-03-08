import pytest

import taipy.core.taipy as tp
from taipy.core.common.frequency import Frequency
from taipy.core.cycle.cycle import Cycle
from taipy.core.exceptions.configuration import InvalidConfigurationId


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

    tp.set(cycle)
    cycle.properties["qux"] = 5
    same_cycle = tp.get(cycle.id)
    assert cycle.properties["qux"] == 5
    assert same_cycle.properties["qux"] == 5
