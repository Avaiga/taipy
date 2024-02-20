# Copyright 2021-2024 Avaiga Private Limited
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

from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_id import CycleId
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager import _JobManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.task._task_manager import _TaskManager


def test_save_and_get_cycle_entity(init_sql_repo, cycle, current_datetime):
    _CycleManager._repository = _CycleManagerFactory._build_repository()

    _CycleManager._delete_all()
    assert len(_CycleManager._get_all()) == 0

    _CycleManager._set(cycle)
    assert _CycleManager._exists(cycle.id)

    cycle_1 = _CycleManager._get(cycle.id)

    assert cycle_1.id == cycle.id
    assert cycle_1.name == cycle.name
    assert cycle_1.properties == cycle.properties
    assert cycle_1.creation_date == cycle.creation_date
    assert cycle_1.start_date == cycle.start_date
    assert cycle_1.end_date == cycle.end_date
    assert cycle_1.frequency == cycle.frequency

    assert len(_CycleManager._get_all()) == 1
    assert _CycleManager._get(cycle.id) == cycle
    assert _CycleManager._get(cycle.id).name == cycle.name
    assert isinstance(_CycleManager._get(cycle.id).creation_date, datetime)
    assert _CycleManager._get(cycle.id).creation_date == cycle.creation_date
    assert _CycleManager._get(cycle.id).frequency == Frequency.DAILY

    cycle_2_id = CycleId("cycle_2")
    assert _CycleManager._get(cycle_2_id) is None
    assert not _CycleManager._exists(cycle_2_id)

    cycle_3 = Cycle(
        Frequency.MONTHLY,
        {},
        creation_date=current_datetime,
        start_date=current_datetime,
        end_date=current_datetime,
        name="bar",
        id=cycle_1.id,
    )

    _CycleManager._set(cycle_3)

    cycle_3 = _CycleManager._get(cycle_1.id)

    assert _CycleManager._exists(cycle_1.id)
    assert len(_CycleManager._get_all()) == 1
    assert cycle_3.id == cycle_1.id
    assert cycle_3.name == cycle_3.name
    assert cycle_3.properties == cycle_3.properties
    assert cycle_3.creation_date == current_datetime
    assert cycle_3.start_date == current_datetime
    assert cycle_3.end_date == current_datetime
    assert cycle_3.frequency == cycle_3.frequency


def test_create_and_delete_cycle_entity(init_sql_repo):
    _CycleManager._repository = _CycleManagerFactory._build_repository()

    _CycleManager._delete_all()
    assert len(_CycleManager._get_all()) == 0

    cycle_1 = _CycleManager._create(Frequency.DAILY, name="foo", key="value", display_name="foo")

    assert cycle_1.id is not None
    assert cycle_1.name == "foo"
    assert cycle_1.properties == {"key": "value", "display_name": "foo"}
    assert cycle_1.creation_date is not None
    assert cycle_1.start_date is not None
    assert cycle_1.end_date is not None
    assert cycle_1.start_date < cycle_1.creation_date < cycle_1.end_date
    assert cycle_1.key == "value"
    assert cycle_1.frequency == Frequency.DAILY

    cycle_1_id = cycle_1.id

    assert _CycleManager._exists(cycle_1.id)
    assert len(_CycleManager._get_all()) == 1
    assert _CycleManager._get(cycle_1_id) == cycle_1
    assert _CycleManager._get(cycle_1_id).name == "foo"
    assert isinstance(_CycleManager._get(cycle_1_id).creation_date, datetime)
    assert _CycleManager._get(cycle_1_id).frequency == Frequency.DAILY

    cycle_2_id = CycleId("cycle_2")
    assert _CycleManager._get(cycle_2_id) is None
    assert not _CycleManager._exists(cycle_2_id)

    cycle_3 = _CycleManager._create(Frequency.MONTHLY, "bar")

    assert cycle_3.id is not None
    assert cycle_3.name == "bar"
    assert isinstance(cycle_3.creation_date, datetime)
    assert cycle_3.frequency == Frequency.MONTHLY

    cycle_3_id = cycle_3.id

    assert _CycleManager._exists(cycle_3_id)
    assert len(_CycleManager._get_all()) == 2
    assert _CycleManager._get(cycle_3_id).name == "bar"

    cycle_4 = _CycleManager._create(Frequency.YEARLY, "baz")
    cycle_4_id = cycle_4.id

    assert _CycleManager._exists(cycle_4_id)
    assert len(_CycleManager._get_all()) == 3

    _CycleManager._delete(cycle_4_id)

    assert len(_CycleManager._get_all()) == 2
    assert not _CycleManager._exists(cycle_4_id)
    assert _CycleManager._get(cycle_4_id) is None

    _CycleManager._delete_all()
    assert len(_CycleManager._get_all()) == 0
    assert not any(_CycleManager._exists(cycle_id) for cycle_id in [cycle_1_id, cycle_3_id, cycle_4_id])


def test_get_cycle_start_date_and_end_date(init_sql_repo):
    _CycleManager._repository = _CycleManagerFactory._build_repository()

    _CycleManager._delete_all()

    creation_date_1 = datetime.fromisoformat("2021-11-11T11:11:01.000001")

    daily_start_date_1 = _CycleManager._get_start_date_of_cycle(Frequency.DAILY, creation_date=creation_date_1)
    weekly_start_date_1 = _CycleManager._get_start_date_of_cycle(Frequency.WEEKLY, creation_date=creation_date_1)
    monthly_start_date_1 = _CycleManager._get_start_date_of_cycle(Frequency.MONTHLY, creation_date=creation_date_1)
    yearly_start_date_1 = _CycleManager._get_start_date_of_cycle(Frequency.YEARLY, creation_date=creation_date_1)

    assert daily_start_date_1 == datetime.fromisoformat("2021-11-11T00:00:00.000000")
    assert weekly_start_date_1 == datetime.fromisoformat("2021-11-08T00:00:00.000000")
    assert monthly_start_date_1 == datetime.fromisoformat("2021-11-01T00:00:00.000000")
    assert yearly_start_date_1 == datetime.fromisoformat("2021-01-01T00:00:00.000000")

    daily_end_date_1 = _CycleManager._get_end_date_of_cycle(Frequency.DAILY, start_date=daily_start_date_1)
    weekly_end_date_1 = _CycleManager._get_end_date_of_cycle(Frequency.WEEKLY, start_date=weekly_start_date_1)
    monthly_end_date_1 = _CycleManager._get_end_date_of_cycle(Frequency.MONTHLY, start_date=monthly_start_date_1)
    yearly_end_date_1 = _CycleManager._get_end_date_of_cycle(Frequency.YEARLY, start_date=yearly_start_date_1)

    assert daily_end_date_1 == datetime.fromisoformat("2021-11-11T23:59:59.999999")
    assert weekly_end_date_1 == datetime.fromisoformat("2021-11-14T23:59:59.999999")
    assert monthly_end_date_1 == datetime.fromisoformat("2021-11-30T23:59:59.999999")
    assert yearly_end_date_1 == datetime.fromisoformat("2021-12-31T23:59:59.999999")

    creation_date_2 = datetime.now()

    daily_start_date_2 = _CycleManager._get_start_date_of_cycle(Frequency.DAILY, creation_date=creation_date_2)
    daily_end_date_2 = _CycleManager._get_end_date_of_cycle(Frequency.DAILY, daily_start_date_2)
    assert daily_start_date_2.date() == creation_date_2.date()
    assert daily_end_date_2.date() == creation_date_2.date()
    assert daily_start_date_2 < creation_date_2 < daily_end_date_2

    weekly_start_date_2 = _CycleManager._get_start_date_of_cycle(Frequency.WEEKLY, creation_date=creation_date_2)
    weekly_end_date_2 = _CycleManager._get_end_date_of_cycle(Frequency.WEEKLY, weekly_start_date_2)
    assert weekly_start_date_2 < creation_date_2 < weekly_end_date_2

    monthly_start_date_2 = _CycleManager._get_start_date_of_cycle(Frequency.MONTHLY, creation_date=creation_date_2)
    monthly_end_date_2 = _CycleManager._get_end_date_of_cycle(Frequency.MONTHLY, monthly_start_date_2)
    assert monthly_start_date_2.month == creation_date_2.month and monthly_start_date_2.day == 1
    assert monthly_end_date_2.month == creation_date_2.month
    assert monthly_start_date_2 < creation_date_2 < monthly_end_date_2

    yearly_start_date_2 = _CycleManager._get_start_date_of_cycle(Frequency.YEARLY, creation_date=creation_date_2)
    yearly_end_date_2 = _CycleManager._get_end_date_of_cycle(Frequency.YEARLY, yearly_start_date_2)
    assert yearly_start_date_2.year == creation_date_2.year
    assert yearly_start_date_2 == datetime(creation_date_2.year, 1, 1)
    assert yearly_end_date_2.year == creation_date_2.year
    assert yearly_end_date_2.date() == datetime(creation_date_2.year, 12, 31).date()
    assert yearly_start_date_2 < creation_date_2 < yearly_end_date_2


def test_hard_delete_shared_entities(init_sql_repo):
    _ScenarioManager._repository = _ScenarioManagerFactory._build_repository()

    dn_config_1 = Config.configure_data_node("my_input_1", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_config_2 = Config.configure_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_config_3 = Config.configure_data_node("my_input_3", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_config_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_config_1 = Config.configure_task("task_config_1", print, dn_config_1, dn_config_2)
    task_config_2 = Config.configure_task("task_config_2", print, dn_config_2, dn_config_3)
    task_config_3 = Config.configure_task("task_config_3", print, dn_config_3, dn_config_4)  # scope = global
    creation_date = datetime.now()
    scenario_config_1 = Config.configure_scenario(
        "scenario_config_1",
        [task_config_1, task_config_2, task_config_3],
        creation_date=creation_date,
        frequency=Frequency.DAILY,
    )
    scenario_config_1.add_sequences(
        {
            "sequence_1": [task_config_1, task_config_2],
            "sequence_2": [task_config_1, task_config_2],
            "sequence_3": [task_config_3],
        }
    )
    scenario_config_2 = Config.configure_scenario(
        "scenario_config_2", [task_config_2, task_config_3]
    )  # No Frequency so cycle attached to scenarios
    scenario_config_2.add_sequences({"sequence_3": [task_config_3]})

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    scenario_2 = _ScenarioManager._create(scenario_config_1)
    scenario_3 = _ScenarioManager._create(scenario_config_2)
    scenario_1.submit()
    scenario_2.submit()
    scenario_3.submit()

    assert len(_ScenarioManager._get_all()) == 3
    assert len(_SequenceManager._get_all()) == 7
    assert len(_TaskManager._get_all()) == 7
    assert len(_DataManager._get_all()) == 8
    assert len(_JobManager._get_all()) == 8
    assert len(_CycleManager._get_all()) == 1
    _CycleManager._hard_delete(scenario_1.cycle.id)
    assert len(_CycleManager._get_all()) == 0
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
