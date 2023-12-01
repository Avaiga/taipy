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

import os
from datetime import datetime, timedelta
from time import sleep
from unittest import mock

import pytest
import src.taipy.core as tp
from src.taipy.config import Config
from src.taipy.config.common.scope import Scope
from src.taipy.config.exceptions.exceptions import InvalidConfigurationId
from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.data_node_id import DataNodeId
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import DataNodeIsBeingEdited, NoData
from src.taipy.core.job.job_id import JobId

from .utils import FakeDataNode


def funct_a_b(input: str):
    print("task_a_b")
    return "B"


def funct_b_c(input: str):
    print("task_b_c")
    return "C"


def funct_b_d(input: str):
    print("task_b_d")
    return "D"


class TestDataNode:
    def test_create_with_default_values(self):
        dn = DataNode("foo_bar")
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.name is None
        assert dn.owner_id is None
        assert dn.parent_ids == set()
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert len(dn.properties) == 0

    def test_create(self):
        a_date = datetime.now()
        dn = DataNode(
            "foo_bar",
            Scope.SCENARIO,
            DataNodeId("an_id"),
            "a_scenario_id",
            {"a_parent_id"},
            a_date,
            [dict(job_id="a_job_id")],
            edit_in_progress=False,
            prop="erty",
            name="a name",
        )
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id == "an_id"
        assert dn.name == "a name"
        assert dn.owner_id == "a_scenario_id"
        assert dn.parent_ids == {"a_parent_id"}
        assert dn.last_edit_date == a_date
        assert dn.job_ids == ["a_job_id"]
        assert dn.is_ready_for_reading
        assert len(dn.properties) == 2
        assert dn.properties == {"prop": "erty", "name": "a name"}

        with pytest.raises(InvalidConfigurationId):
            DataNode("foo bar")

    def test_read_write(self):
        dn = FakeDataNode("foo_bar")
        with pytest.raises(NoData):
            assert dn.read() is None
            dn.read_or_raise()
        assert dn.write_has_been_called == 0
        assert dn.read_has_been_called == 0
        assert not dn.is_ready_for_reading
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert dn.edits == []

        dn.write("Any data")
        assert dn.write_has_been_called == 1
        assert dn.read_has_been_called == 0
        assert dn.last_edit_date is not None
        first_edition = dn.last_edit_date
        assert dn.is_ready_for_reading
        assert dn.job_ids == []
        assert len(dn.edits) == 1
        assert dn.get_last_edit()["timestamp"] == dn.last_edit_date

        sleep(0.1)

        dn.write("Any other data", job_id := JobId("a_job_id"))
        assert dn.write_has_been_called == 2
        assert dn.read_has_been_called == 0
        second_edition = dn.last_edit_date
        assert first_edition < second_edition
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]
        assert len(dn.edits) == 2
        assert dn.get_last_edit()["timestamp"] == dn.last_edit_date

        dn.read()
        assert dn.write_has_been_called == 2
        assert dn.read_has_been_called == 1
        second_edition = dn.last_edit_date
        assert first_edition < second_edition
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

    def test_lock_initialization(self):
        dn = InMemoryDataNode("dn", Scope.SCENARIO)
        assert not dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None

    def test_locked_dn_unlockable_only_by_same_editor(self):
        dn = InMemoryDataNode("dn", Scope.SCENARIO)
        dn.lock_edit("user_1")
        assert dn.edit_in_progress
        assert dn._editor_id == "user_1"
        assert dn._editor_expiration_date is not None
        with pytest.raises(DataNodeIsBeingEdited):
            dn.lock_edit("user_2")
        with pytest.raises(DataNodeIsBeingEdited):
            dn.unlock_edit("user_2")
        dn.unlock_edit("user_1")
        assert not dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None

    def test_none_editor_can_lock_a_locked_dn(self):
        dn = InMemoryDataNode("dn", Scope.SCENARIO)
        dn.lock_edit("user")
        assert dn.edit_in_progress
        assert dn._editor_id == "user"
        assert dn._editor_expiration_date is not None
        dn.lock_edit()
        assert dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None

    def test_none_editor_can_unlock_a_locked_dn(self):
        dn = InMemoryDataNode("dn", Scope.SCENARIO)
        dn.lock_edit("user")
        assert dn.edit_in_progress
        assert dn._editor_id == "user"
        assert dn._editor_expiration_date is not None
        dn.unlock_edit()
        assert not dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None

        dn.lock_edit()
        assert dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None
        dn.unlock_edit()
        assert not dn.edit_in_progress
        assert dn._editor_id is None
        assert dn._editor_expiration_date is None

    def test_ready_for_reading(self):
        dn = InMemoryDataNode("foo_bar", Scope.CYCLE)
        assert dn.last_edit_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.lock_edit()
        assert dn.last_edit_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.unlock_edit()
        assert dn.last_edit_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.lock_edit()
        assert dn.last_edit_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.write("toto", job_id := JobId("a_job_id"))
        assert dn.last_edit_date is not None
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

    def test_is_valid_no_validity_period(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.SCENARIO, DataNodeId("id"), "name", "owner_id")
        assert not dn.is_valid

        # test has been writen
        dn.write("My data")
        assert dn.is_valid

    def test_is_valid_with_30_min_validity_period(self):
        # Test Never been writen
        dn = InMemoryDataNode(
            "foo", Scope.SCENARIO, DataNodeId("id"), "name", "owner_id", validity_period=timedelta(minutes=30)
        )
        assert dn.is_valid is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn.is_valid is True

        # Has been writen more than 30 minutes ago
        dn.last_edit_date = datetime.now() + timedelta(days=-1)
        assert dn.is_valid is False

    def test_is_valid_with_5_days_validity_period(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.SCENARIO, validity_period=timedelta(days=5))
        assert dn.is_valid is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn.is_valid is True

        # Has been writen more than 30 minutes ago
        dn._last_edit_date = datetime.now() - timedelta(days=6)
        _DataManager()._set(dn)
        assert dn.is_valid is False

    def test_is_up_to_date(self, current_datetime):
        dn_confg_1 = Config.configure_in_memory_data_node("dn_1")
        dn_confg_2 = Config.configure_in_memory_data_node("dn_2")
        dn_confg_3 = Config.configure_in_memory_data_node("dn_3", scope=Scope.GLOBAL)
        task_config_1 = Config.configure_task("t1", print, [dn_confg_1], [dn_confg_2])
        task_config_2 = Config.configure_task("t2", print, [dn_confg_2], [dn_confg_3])
        scenario_config = Config.configure_scenario("sc", [task_config_1, task_config_2])

        scenario_1 = tp.create_scenario(scenario_config)
        assert len(_DataManager._get_all()) == 3

        dn_1_1 = scenario_1.data_nodes["dn_1"]
        dn_2_1 = scenario_1.data_nodes["dn_2"]
        dn_3_1 = scenario_1.data_nodes["dn_3"]

        assert dn_1_1.last_edit_date is None
        assert dn_2_1.last_edit_date is None
        assert dn_3_1.last_edit_date is None

        dn_1_1.last_edit_date = current_datetime + timedelta(1)
        dn_2_1.last_edit_date = current_datetime + timedelta(2)
        dn_3_1.last_edit_date = current_datetime + timedelta(3)
        assert dn_1_1.is_up_to_date
        assert dn_2_1.is_up_to_date
        assert dn_3_1.is_up_to_date

        dn_2_1.last_edit_date = current_datetime + timedelta(4)
        assert dn_1_1.is_up_to_date
        assert dn_2_1.is_up_to_date
        assert not dn_3_1.is_up_to_date

        dn_1_1.last_edit_date = current_datetime + timedelta(5)
        assert dn_1_1.is_up_to_date
        assert not dn_2_1.is_up_to_date
        assert not dn_3_1.is_up_to_date

        dn_1_1.last_edit_date = current_datetime + timedelta(1)
        dn_2_1.last_edit_date = current_datetime + timedelta(2)
        dn_3_1.last_edit_date = current_datetime + timedelta(3)

    def test_is_up_to_date_across_scenarios(self, current_datetime):
        dn_confg_1 = Config.configure_in_memory_data_node("dn_1", scope=Scope.SCENARIO)
        dn_confg_2 = Config.configure_in_memory_data_node("dn_2", scope=Scope.SCENARIO)
        dn_confg_3 = Config.configure_in_memory_data_node("dn_3", scope=Scope.GLOBAL)
        task_config_1 = Config.configure_task("t1", print, [dn_confg_1], [dn_confg_2])
        task_config_2 = Config.configure_task("t2", print, [dn_confg_2], [dn_confg_3])
        scenario_config = Config.configure_scenario("sc", [task_config_1, task_config_2])

        scenario_1 = tp.create_scenario(scenario_config)
        scenario_2 = tp.create_scenario(scenario_config)
        assert len(_DataManager._get_all()) == 5

        dn_1_1 = scenario_1.data_nodes["dn_1"]
        dn_2_1 = scenario_1.data_nodes["dn_2"]
        dn_1_2 = scenario_2.data_nodes["dn_1"]
        dn_2_2 = scenario_2.data_nodes["dn_2"]
        dn_3 = scenario_1.data_nodes["dn_3"]
        assert dn_3 == scenario_2.data_nodes["dn_3"]

        assert dn_1_1.last_edit_date is None
        assert dn_2_1.last_edit_date is None
        assert dn_1_2.last_edit_date is None
        assert dn_2_2.last_edit_date is None
        assert dn_3.last_edit_date is None

        dn_1_1.last_edit_date = current_datetime + timedelta(1)
        dn_2_1.last_edit_date = current_datetime + timedelta(2)
        dn_1_2.last_edit_date = current_datetime + timedelta(3)
        dn_2_2.last_edit_date = current_datetime + timedelta(4)
        dn_3.last_edit_date = current_datetime + timedelta(5)
        assert dn_1_1.is_up_to_date
        assert dn_2_1.is_up_to_date
        assert dn_1_2.is_up_to_date
        assert dn_2_2.is_up_to_date
        assert dn_3.is_up_to_date

        dn_2_1.last_edit_date = current_datetime + timedelta(6)
        assert dn_1_1.is_up_to_date
        assert dn_2_1.is_up_to_date
        assert dn_1_2.is_up_to_date
        assert dn_2_2.is_up_to_date
        assert not dn_3.is_up_to_date

        dn_2_1.last_edit_date = current_datetime + timedelta(2)
        dn_2_2.last_edit_date = current_datetime + timedelta(6)
        assert dn_1_1.is_up_to_date
        assert dn_2_1.is_up_to_date
        assert dn_1_2.is_up_to_date
        assert dn_2_2.is_up_to_date
        assert not dn_3.is_up_to_date

        dn_2_2.last_edit_date = current_datetime + timedelta(4)
        dn_1_1.last_edit_date = current_datetime + timedelta(6)
        assert dn_1_1.is_up_to_date
        assert not dn_2_1.is_up_to_date
        assert dn_1_2.is_up_to_date
        assert dn_2_2.is_up_to_date
        assert not dn_3.is_up_to_date

        dn_1_2.last_edit_date = current_datetime + timedelta(6)
        assert dn_1_1.is_up_to_date
        assert not dn_2_1.is_up_to_date
        assert dn_1_2.is_up_to_date
        assert not dn_2_2.is_up_to_date
        assert not dn_3.is_up_to_date

    def test_do_not_recompute_data_node_valid_but_continue_sequence_execution(self):
        Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

        a = Config.configure_data_node("A", "pickle", default_data="A")
        b = Config.configure_data_node("B", "pickle")
        c = Config.configure_data_node("C", "pickle")
        d = Config.configure_data_node("D", "pickle")

        task_a_b = Config.configure_task("task_a_b", funct_a_b, input=a, output=b, skippable=True)
        task_b_c = Config.configure_task("task_b_c", funct_b_c, input=b, output=c)
        task_b_d = Config.configure_task("task_b_d", funct_b_d, input=b, output=d)
        scenario_cfg = Config.configure_scenario("scenario", [task_a_b, task_b_c, task_b_d])

        _OrchestratorFactory._build_dispatcher()

        scenario = tp.create_scenario(scenario_cfg)
        scenario.submit()
        assert scenario.A.read() == "A"
        assert scenario.B.read() == "B"
        assert scenario.C.read() == "C"
        assert scenario.D.read() == "D"

        scenario.submit()

        assert len(tp.get_jobs()) == 6
        jobs_and_status = [(job.task.config_id, job.status) for job in tp.get_jobs()]
        assert ("task_a_b", tp.Status.COMPLETED) in jobs_and_status
        assert ("task_a_b", tp.Status.SKIPPED) in jobs_and_status
        assert ("task_b_c", tp.Status.COMPLETED) in jobs_and_status
        assert ("task_b_d", tp.Status.COMPLETED) in jobs_and_status

    def test_data_node_update_after_writing(self):
        dn = FakeDataNode("foo")

        _DataManager._set(dn)
        assert not _DataManager._get(dn.id).is_ready_for_reading
        dn.write("Any data")

        assert dn.is_ready_for_reading
        assert _DataManager._get(dn.id).is_ready_for_reading

    def test_expiration_date_raise_if_never_write(self):
        dn = FakeDataNode("foo")

        with pytest.raises(NoData):
            dn.expiration_date

    def test_validity_null_if_never_write(self):
        dn = FakeDataNode("foo")

        assert dn.validity_period is None

    def test_auto_set_and_reload(self, current_datetime):
        dn_1 = InMemoryDataNode(
            "foo",
            scope=Scope.GLOBAL,
            id=DataNodeId("an_id"),
            owner_id=None,
            parent_ids=None,
            last_edit_date=current_datetime,
            edits=[dict(job_id="a_job_id")],
            edit_in_progress=False,
            validity_period=None,
            properties={
                "name": "foo",
            },
        )

        dm = _DataManager()
        dm._set(dn_1)

        dn_2 = dm._get(dn_1)

        # auto set & reload on scope attribute
        assert dn_1.scope == Scope.GLOBAL
        assert dn_2.scope == Scope.GLOBAL
        dn_1.scope = Scope.CYCLE
        assert dn_1.scope == Scope.CYCLE
        assert dn_2.scope == Scope.CYCLE
        dn_2.scope = Scope.SCENARIO
        assert dn_1.scope == Scope.SCENARIO
        assert dn_2.scope == Scope.SCENARIO

        new_datetime = current_datetime + timedelta(1)
        new_datetime_1 = current_datetime + timedelta(3)

        # auto set & reload on last_edit_date attribute
        assert dn_1.last_edit_date == current_datetime
        assert dn_2.last_edit_date == current_datetime
        dn_1.last_edit_date = new_datetime_1
        assert dn_1.last_edit_date == new_datetime_1
        assert dn_2.last_edit_date == new_datetime_1
        dn_2.last_edit_date = new_datetime
        assert dn_1.last_edit_date == new_datetime
        assert dn_2.last_edit_date == new_datetime

        # auto set & reload on name attribute
        assert dn_1.name == "foo"
        assert dn_2.name == "foo"
        dn_1.name = "fed"
        assert dn_1.name == "fed"
        assert dn_2.name == "fed"
        dn_2.name = "def"
        assert dn_1.name == "def"
        assert dn_2.name == "def"

        # auto set & reload on parent_ids attribute (set() object does not have auto set yet)
        assert dn_1.parent_ids == set()
        assert dn_2.parent_ids == set()
        dn_1._parent_ids.update(["sc2"])
        _DataManager._set(dn_1)
        assert dn_1.parent_ids == {"sc2"}
        assert dn_2.parent_ids == {"sc2"}
        dn_2._parent_ids.clear()
        dn_2._parent_ids.update(["sc1"])
        _DataManager._set(dn_2)
        assert dn_1.parent_ids == {"sc1"}
        assert dn_2.parent_ids == {"sc1"}

        # auto set & reload on edit_in_progress attribute
        assert not dn_2.edit_in_progress
        assert not dn_1.edit_in_progress
        dn_1.edit_in_progress = True
        assert dn_1.edit_in_progress
        assert dn_2.edit_in_progress
        dn_2.unlock_edit()
        assert not dn_1.edit_in_progress
        assert not dn_2.edit_in_progress
        dn_1.lock_edit()
        assert dn_1.edit_in_progress
        assert dn_2.edit_in_progress

        # auto set & reload on validity_period attribute
        time_period_1 = timedelta(1)
        time_period_2 = timedelta(5)
        assert dn_1.validity_period is None
        assert dn_2.validity_period is None
        dn_1.validity_period = time_period_1
        assert dn_1.validity_period == time_period_1
        assert dn_2.validity_period == time_period_1
        dn_2.validity_period = time_period_2
        assert dn_1.validity_period == time_period_2
        assert dn_2.validity_period == time_period_2

        # auto set & reload on properties attribute
        assert dn_1.properties == {"name": "def"}
        assert dn_2.properties == {"name": "def"}
        dn_1._properties["qux"] = 4
        assert dn_1.properties["qux"] == 4
        assert dn_2.properties["qux"] == 4

        assert dn_1.properties == {"qux": 4, "name": "def"}
        assert dn_2.properties == {"qux": 4, "name": "def"}
        dn_2._properties["qux"] = 5
        assert dn_1.properties["qux"] == 5
        assert dn_2.properties["qux"] == 5

        dn_1.properties["temp_key_1"] = "temp_value_1"
        dn_1.properties["temp_key_2"] = "temp_value_2"
        assert dn_1.properties == {
            "name": "def",
            "qux": 5,
            "temp_key_1": "temp_value_1",
            "temp_key_2": "temp_value_2",
        }
        assert dn_2.properties == {
            "name": "def",
            "qux": 5,
            "temp_key_1": "temp_value_1",
            "temp_key_2": "temp_value_2",
        }
        dn_1.properties.pop("temp_key_1")
        assert "temp_key_1" not in dn_1.properties.keys()
        assert "temp_key_1" not in dn_1.properties.keys()
        assert dn_1.properties == {
            "name": "def",
            "qux": 5,
            "temp_key_2": "temp_value_2",
        }
        assert dn_2.properties == {
            "name": "def",
            "qux": 5,
            "temp_key_2": "temp_value_2",
        }
        dn_2.properties.pop("temp_key_2")
        assert dn_1.properties == {
            "qux": 5,
            "name": "def",
        }
        assert dn_2.properties == {
            "qux": 5,
            "name": "def",
        }
        assert "temp_key_2" not in dn_1.properties.keys()
        assert "temp_key_2" not in dn_2.properties.keys()

        dn_1.properties["temp_key_3"] = 0
        assert dn_1.properties == {
            "qux": 5,
            "temp_key_3": 0,
            "name": "def",
        }
        assert dn_2.properties == {
            "qux": 5,
            "temp_key_3": 0,
            "name": "def",
        }
        dn_1.properties.update({"temp_key_3": 1})
        assert dn_1.properties == {
            "qux": 5,
            "temp_key_3": 1,
            "name": "def",
        }
        assert dn_2.properties == {
            "qux": 5,
            "temp_key_3": 1,
            "name": "def",
        }
        dn_1.properties.update(dict())
        assert dn_1.properties == {
            "qux": 5,
            "temp_key_3": 1,
            "name": "def",
        }
        assert dn_2.properties == {
            "qux": 5,
            "temp_key_3": 1,
            "name": "def",
        }
        dn_1.properties["temp_key_4"] = 0
        dn_1.properties["temp_key_5"] = 0

        dn_1.last_edit_date = new_datetime

        assert len(dn_1.job_ids) == 1
        assert len(dn_2.job_ids) == 1

        with dn_1 as dn:
            assert dn.config_id == "foo"
            assert dn.owner_id is None
            assert dn.scope == Scope.SCENARIO
            assert dn.last_edit_date == new_datetime
            assert dn.name == "def"
            assert dn.edit_in_progress
            assert dn.validity_period == time_period_2
            assert len(dn.job_ids) == 1
            assert dn._is_in_context
            assert dn.properties["qux"] == 5
            assert dn.properties["temp_key_3"] == 1
            assert dn.properties["temp_key_4"] == 0
            assert dn.properties["temp_key_5"] == 0

            new_datetime_2 = new_datetime + timedelta(5)

            dn.scope = Scope.CYCLE
            dn.last_edit_date = new_datetime_2
            dn.name = "abc"
            dn.edit_in_progress = False
            dn.validity_period = None
            dn.properties["qux"] = 9
            dn.properties.pop("temp_key_3")
            dn.properties.pop("temp_key_4")
            dn.properties.update({"temp_key_4": 1})
            dn.properties.update({"temp_key_5": 2})
            dn.properties.pop("temp_key_5")
            dn.properties.update(dict())

            assert dn.config_id == "foo"
            assert dn.owner_id is None
            assert dn.scope == Scope.SCENARIO
            assert dn.last_edit_date == new_datetime
            assert dn.name == "def"
            assert dn.edit_in_progress
            assert dn.validity_period == time_period_2
            assert len(dn.job_ids) == 1
            assert dn.properties["qux"] == 5
            assert dn.properties["temp_key_3"] == 1
            assert dn.properties["temp_key_4"] == 0
            assert dn.properties["temp_key_5"] == 0

        assert dn_1.config_id == "foo"
        assert dn_1.owner_id is None
        assert dn_1.scope == Scope.CYCLE
        assert dn_1.last_edit_date == new_datetime_2
        assert dn_1.name == "abc"
        assert not dn_1.edit_in_progress
        assert dn_1.validity_period is None
        assert not dn_1._is_in_context
        assert len(dn_1.job_ids) == 1
        assert dn_1.properties["qux"] == 9
        assert "temp_key_3" not in dn_1.properties.keys()
        assert dn_1.properties["temp_key_4"] == 1
        assert "temp_key_5" not in dn_1.properties.keys()

    def test_get_parents(self, data_node):
        with mock.patch("src.taipy.core.get_parents") as mck:
            data_node.get_parents()
            mck.assert_called_once_with(data_node)

    def test_cacheable_deprecated_false(self):
        dn = FakeDataNode("foo")
        with pytest.warns(DeprecationWarning):
            dn.cacheable
        assert dn.cacheable is False

    def test_cacheable_deprecated_true(self):
        dn = FakeDataNode("foo", properties={"cacheable": True})
        with pytest.warns(DeprecationWarning):
            dn.cacheable
        assert dn.cacheable is True

    def test_data_node_with_env_variable_value_not_stored(self):
        dn_config = Config.configure_data_node("A", prop="ENV[FOO]")
        with mock.patch.dict(os.environ, {"FOO": "bar"}):
            dn = _DataManager._bulk_get_or_create([dn_config])[dn_config]
            assert dn._properties.data["prop"] == "ENV[FOO]"
            assert dn.properties["prop"] == "bar"
            assert dn.prop == "bar"

    def test_path_populated_with_config_default_path(self):
        dn_config = Config.configure_data_node("data_node", "pickle", default_path="foo.p")
        assert dn_config.default_path == "foo.p"
        data_node = _DataManager._bulk_get_or_create([dn_config])[dn_config]
        assert data_node.path == "foo.p"
        data_node.path = "baz.p"
        assert data_node.path == "baz.p"

    def test_track_edit(self):
        dn_config = Config.configure_data_node("A")
        data_node = _DataManager._bulk_get_or_create([dn_config])[dn_config]

        data_node.write(data="1", job_id="job_1")
        data_node.write(data="2", job_id="job_1")
        data_node.write(data="3", job_id="job_1")

        assert len(data_node.edits) == 3
        assert len(data_node.job_ids) == 3
        assert data_node.edits[-1] == data_node.get_last_edit()
        assert data_node.last_edit_date == data_node.get_last_edit().get("timestamp")

        date = datetime(2050, 1, 1, 12, 12)
        data_node.write(data="4", timestamp=date, message="This is a comment on this edit", env="staging")

        assert len(data_node.edits) == 4
        assert len(data_node.job_ids) == 3
        assert data_node.edits[-1] == data_node.get_last_edit()

        last_edit = data_node.get_last_edit()
        assert last_edit["message"] == "This is a comment on this edit"
        assert last_edit["env"] == "staging"
        assert last_edit["timestamp"] == date

    def test_label(self):
        a_date = datetime.now()
        dn = DataNode(
            "foo_bar",
            Scope.SCENARIO,
            DataNodeId("an_id"),
            "a_scenario_id",
            {"a_parent_id"},
            a_date,
            [dict(job_id="a_job_id")],
            edit_in_progress=False,
            prop="erty",
            name="a name",
        )
        with mock.patch("src.taipy.core.get") as get_mck:

            class MockOwner:
                label = "owner_label"

                def get_label(self):
                    return self.label

            get_mck.return_value = MockOwner()
            assert dn.get_label() == "owner_label > " + dn.name
            assert dn.get_simple_label() == dn.name

    def test_explicit_label(self):
        a_date = datetime.now()
        dn = DataNode(
            "foo_bar",
            Scope.SCENARIO,
            DataNodeId("an_id"),
            "a_scenario_id",
            {"a_parent_id"},
            a_date,
            [dict(job_id="a_job_id")],
            edit_in_progress=False,
            label="a label",
            name="a name",
        )
        assert dn.get_label() == "a label"
        assert dn.get_simple_label() == "a label"

    def test_change_data_node_name(self):
        cgf = Config.configure_data_node("foo", scope=Scope.GLOBAL)
        dn = tp.create_global_data_node(cgf)

        dn.name = "bar"
        assert dn.name == "bar"

        # This new syntax will be the only one allowed: https://github.com/Avaiga/taipy-core/issues/806
        dn.properties["name"] = "baz"
        assert dn.name == "baz"
