from datetime import datetime

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency


def test_create_cycle_entity(current_datetime):

    cycle_entity_1 = Cycle("fOo   ", Frequency.DAILY, {"key": "value"})
    assert cycle_entity_1.id is not None
    assert cycle_entity_1.config_name == "foo"
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
    assert cycle_entity_2.config_name == "bar-xea"
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


def test_to_model(current_datetime):
    cycle_entity_1 = Cycle(
        "cycle_name_1",
        Frequency.QUARTERLY,
        {"key": "value"},
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
        cycle_id=CycleId("cycle_id_1"),
    )

    model = cycle_entity_1.to_model()
    assert model.id == "cycle_id_1"
    assert model.name == "cycle_name_1"
    assert model.creation_date == current_datetime.isoformat()
    assert model.start_date == current_datetime.isoformat()
    assert model.end_date == current_datetime.isoformat()
    assert len(model.properties) == 1
    assert model.properties["key"] == "value"

    cycle_entity_2 = Cycle(
        "cycle_name_2",
        Frequency.QUARTERLY,
        {},
        cycle_id=CycleId("cycle_id_2"),
    )

    model_2 = cycle_entity_2.to_model()
    assert model_2.id == "cycle_id_2"
    assert model_2.name == "cycle_name_2"
    assert isinstance(model_2.creation_date, str)
    assert model_2.start_date is None
    assert model_2.end_date is None
    assert len(model_2.properties) == 0
