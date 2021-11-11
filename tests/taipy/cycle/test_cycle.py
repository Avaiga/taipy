from datetime import datetime

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency


def test_create_cycle_entity(current_datetime):

    cycle_entity_1 = Cycle("fOo   ", Frequency.DAILY, {"key": "value"})
    assert cycle_entity_1.id is not None
    assert cycle_entity_1.name == "foo"
    assert cycle_entity_1.properties == {"key": "value"}
    assert cycle_entity_1.creation_date is not None
    assert cycle_entity_1.start_date is None
    assert cycle_entity_1.end_date is None
    assert cycle_entity_1.key == "value"
    assert cycle_entity_1.frequency == Frequency.DAILY

    cycle_entity_2 = Cycle(
        "   bar/ξéà   ",
        Frequency.MONTHLY,
        {},
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
    )
    assert cycle_entity_2.name == "bar-xea"
    assert cycle_entity_2.frequency == Frequency.MONTHLY
    assert cycle_entity_2.creation_date == current_datetime
    assert cycle_entity_2.start_date == current_datetime
    assert cycle_entity_2.end_date == current_datetime


def test_add_property_to_scenario():
    cycle_1 = Cycle("foo", Frequency.DAILY, {"key": "value"})
    assert cycle_1.properties == {"key": "value"}
    assert cycle_1.key == "value"

    cycle_1.properties["new_key"] = "new_value"

    assert cycle_1.properties == {"key": "value", "new_key": "new_value"}
    assert cycle_1.key == "value"
    assert cycle_1.new_key == "new_value"
