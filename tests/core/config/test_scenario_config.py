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
from unittest import mock

import pytest

from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def my_func():
    pass


def test_scenario_creation():
    dn_config_1 = Config.configure_data_node("dn1")
    dn_config_2 = Config.configure_data_node("dn2")
    dn_config_3 = Config.configure_data_node("dn3")
    dn_config_4 = Config.configure_data_node("dn4")
    task_config_1 = Config.configure_task("task1", sum, [dn_config_1, dn_config_2], dn_config_3)
    task_config_2 = Config.configure_task("task2", print, dn_config_3)
    scenario = Config.configure_scenario(
        "scenarios1", [task_config_1, task_config_2], [dn_config_4], comparators={"dn_cfg": [my_func]}
    )

    assert list(Config.scenarios) == ["default", scenario.id]

    scenario2 = Config.configure_scenario("scenarios2", [task_config_1], frequency=Frequency.MONTHLY)
    assert list(Config.scenarios) == ["default", scenario.id, scenario2.id]


def test_scenario_count():
    task_config_1 = Config.configure_task("task1", my_func)
    task_config_2 = Config.configure_task("task2", print)
    Config.configure_scenario("scenarios1", [task_config_1, task_config_2])
    assert len(Config.scenarios) == 2

    Config.configure_scenario("scenarios2", [task_config_1])
    assert len(Config.scenarios) == 3

    Config.configure_scenario("scenarios3", [task_config_2])
    assert len(Config.scenarios) == 4


def test_scenario_getitem():
    dn_config_1 = Config.configure_data_node("dn1")
    dn_config_2 = Config.configure_data_node("dn2")
    dn_config_3 = Config.configure_data_node("dn3")
    dn_config_4 = Config.configure_data_node("dn4")
    task_config_1 = Config.configure_task("task1", sum, [dn_config_1, dn_config_2], dn_config_3)
    task_config_2 = Config.configure_task("task2", print, dn_config_3)
    scenario_id = "scenarios1"
    scenario = Config.configure_scenario(scenario_id, [task_config_1, task_config_2], [dn_config_4])

    assert Config.scenarios[scenario_id].id == scenario.id

    assert Config.scenarios[scenario_id].task_configs == scenario.task_configs
    assert Config.scenarios[scenario_id].tasks == scenario.tasks
    assert Config.scenarios[scenario_id].task_configs == scenario.tasks

    assert Config.scenarios[scenario_id].additional_data_node_configs == scenario.additional_data_node_configs
    assert Config.scenarios[scenario_id].additional_data_nodes == scenario.additional_data_nodes
    assert Config.scenarios[scenario_id].additional_data_node_configs == scenario.additional_data_nodes

    assert Config.scenarios[scenario_id].data_node_configs == scenario.data_node_configs
    assert Config.scenarios[scenario_id].data_nodes == scenario.data_nodes
    assert Config.scenarios[scenario_id].data_node_configs == scenario.data_nodes

    assert scenario.tasks == [task_config_1, task_config_2]
    assert scenario.additional_data_node_configs == [dn_config_4]
    assert scenario.data_nodes == set([dn_config_4, dn_config_1, dn_config_2, dn_config_3])

    assert Config.scenarios[scenario_id].properties == scenario.properties


def test_scenario_creation_no_duplication():
    task_config_1 = Config.configure_task("task1", my_func)
    task_config_2 = Config.configure_task("task2", print)
    dn_config = Config.configure_data_node("dn")
    Config.configure_scenario("scenarios1", [task_config_1, task_config_2], [dn_config])

    assert len(Config.scenarios) == 2

    Config.configure_scenario("scenarios1", [task_config_1, task_config_2], [dn_config])
    assert len(Config.scenarios) == 2


def test_scenario_get_set_and_remove_comparators():
    task_config_1 = Config.configure_task("task1", my_func)
    task_config_2 = Config.configure_task("task2", print)
    dn_config_1 = "dn_config_1"
    scenario_config_1 = Config.configure_scenario(
        "scenarios1", [task_config_1, task_config_2], comparators={dn_config_1: my_func}
    )

    assert scenario_config_1.comparators is not None
    assert scenario_config_1.comparators[dn_config_1] == [my_func]
    assert len(scenario_config_1.comparators.keys()) == 1

    dn_config_2 = "dn_config_2"
    scenario_config_1.add_comparator(dn_config_2, my_func)
    assert len(scenario_config_1.comparators.keys()) == 2

    scenario_config_1.delete_comparator(dn_config_1)
    assert len(scenario_config_1.comparators.keys()) == 1

    scenario_config_1.delete_comparator(dn_config_2)
    assert len(scenario_config_1.comparators.keys()) == 0

    scenario_config_2 = Config.configure_scenario("scenarios2", [task_config_1, task_config_2])

    assert scenario_config_2.comparators is not None

    scenario_config_2.add_comparator(dn_config_1, my_func)
    assert len(scenario_config_2.comparators.keys()) == 1

    scenario_config_2.delete_comparator("dn_config_3")


def test_scenario_config_with_env_variable_value():
    task_config_1 = Config.configure_task("task1", my_func)
    task_config_2 = Config.configure_task("task2", print)
    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        Config.configure_scenario("scenario_name", [task_config_1, task_config_2], prop="ENV[FOO]")
        assert Config.scenarios["scenario_name"].prop == "bar"
        assert Config.scenarios["scenario_name"].properties["prop"] == "bar"
        assert Config.scenarios["scenario_name"]._properties["prop"] == "ENV[FOO]"


def test_clean_config():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    scenario1_config = Config.configure_scenario(
        "id1", [task1_config, task2_config], [], Frequency.YEARLY, {"foo": "bar"}, prop="foo"
    )
    scenario2_config = Config.configure_scenario(
        "id2", [task2_config, task1_config], [], Frequency.MONTHLY, {"foz": "baz"}, prop="bar"
    )

    assert Config.scenarios["id1"] is scenario1_config
    assert Config.scenarios["id2"] is scenario2_config

    scenario1_config._clean()
    scenario2_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.scenarios["id1"] is scenario1_config
    assert Config.scenarios["id2"] is scenario2_config

    assert scenario1_config.id == "id1"
    assert scenario2_config.id == "id2"
    assert scenario1_config.tasks == scenario1_config.task_configs == set()
    assert scenario1_config.additional_data_nodes == scenario1_config.additional_data_node_configs == set()
    assert scenario1_config.data_nodes == scenario1_config.data_node_configs == set()
    assert scenario1_config.frequency is scenario1_config.frequency is None
    assert scenario1_config.comparators == scenario1_config.comparators == {}
    assert scenario1_config.properties == scenario1_config.properties == {}

    assert scenario2_config.tasks == scenario2_config.task_configs == set()
    assert scenario2_config.additional_data_nodes == scenario2_config.additional_data_node_configs == set()
    assert scenario2_config.data_nodes == scenario2_config.data_node_configs == set()
    assert scenario2_config.frequency is scenario2_config.frequency is None
    assert scenario2_config.comparators == scenario2_config.comparators == {}
    assert scenario2_config.properties == scenario2_config.properties == {}
