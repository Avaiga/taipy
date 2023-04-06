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
import datetime
from datetime import timedelta

from src.taipy.core import CycleId
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.cycle.cycle import Cycle
from taipy.config.common.frequency import Frequency


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
    assert cycle_2.name == current_datetime.strftime("%Y")
    assert cycle_2.frequency == Frequency.YEARLY

    cycle_3 = Cycle(Frequency.MONTHLY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_3.name == current_datetime.strftime("%B %Y")
    assert cycle_3.frequency == Frequency.MONTHLY

    cycle_4 = Cycle(Frequency.WEEKLY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_4.name == current_datetime.strftime("Week %W from %A, %d. %B %Y")
    assert cycle_4.frequency == Frequency.WEEKLY

    cycle_5 = Cycle(Frequency.DAILY, {}, current_datetime, current_datetime, current_datetime)
    assert cycle_5.name == current_datetime.strftime("%A, %d. %B %Y")
    assert cycle_5.frequency == Frequency.DAILY


def test_cycle_name(current_datetime):
    start_date = datetime.datetime(2023, 1, 2)
    cycle = Cycle(Frequency.DAILY, {}, current_datetime, start_date, start_date, "name", CycleId("id"))
    assert cycle.name == "name"
    cycle = Cycle(Frequency.DAILY, {}, current_datetime, start_date, start_date, None, CycleId("id"))
    assert cycle.name == "Monday, 02. January 2023"
    cycle = Cycle(Frequency.WEEKLY, {}, current_datetime, start_date, start_date, None, CycleId("id"))
    assert cycle.name == "Week 01 2023, from 02. January"
    cycle = Cycle(Frequency.MONTHLY, {}, current_datetime, start_date, start_date, None, CycleId("id"))
    assert cycle.name == "January 2023"
    cycle = Cycle(Frequency.QUARTERLY, {}, current_datetime, start_date, start_date, None, CycleId("id"))
    assert cycle.name == "2023 Q1"
    cycle = Cycle(Frequency.YEARLY, {}, current_datetime, start_date, start_date, None, CycleId("id"))
    assert cycle.name == "2023"


def test_cycle_label(current_datetime):
    cycle = Cycle(
        Frequency.DAILY,
        {"key": "value"},
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
    )
    assert cycle.get_label() == cycle.name
    assert cycle.get_simple_label() == cycle.name

    cycle._properties["label"] = "label"
    assert cycle.get_label() == "label"
    assert cycle.get_simple_label() == "label"


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
