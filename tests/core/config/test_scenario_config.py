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
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    scenario = Config.configure_scenario(
        "scenarios1", [pipeline1_config, pipeline2_config], comparators={"dn_cfg": [my_func]}
    )

    assert list(Config.scenarios) == ["default", scenario.id]

    scenario2 = Config.configure_scenario("scenarios2", [pipeline1_config, pipeline2_config], Frequency.MONTHLY)
    assert list(Config.scenarios) == ["default", scenario.id, scenario2.id]


def test_scenario_count():
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    Config.configure_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 2

    Config.configure_scenario("scenarios2", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 3

    Config.configure_scenario("scenarios3", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 4


def test_scenario_getitem():
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    scenario_id = "scenarios1"
    scenario = Config.configure_scenario(scenario_id, [pipeline1_config, pipeline2_config])

    assert Config.scenarios[scenario_id].id == scenario.id
    assert Config.scenarios[scenario_id]._pipelines == scenario._pipelines
    assert Config.scenarios[scenario_id].properties == scenario.properties


def test_scenario_creation_no_duplication():
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    Config.configure_scenario("scenarios1", [pipeline1_config, pipeline2_config])

    assert len(Config.scenarios) == 2

    Config.configure_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 2


def test_scenario_get_set_and_remove_comparators():
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    dn_config_1 = "dn_config_1"
    scenario_config_1 = Config.configure_scenario(
        "scenarios1", [pipeline1_config, pipeline2_config], comparators={dn_config_1: my_func}
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

    scenario_config_2 = Config.configure_scenario("scenarios2", [pipeline1_config, pipeline2_config])

    assert scenario_config_2.comparators is not None

    scenario_config_2.add_comparator(dn_config_1, my_func)
    assert len(scenario_config_2.comparators.keys()) == 1

    scenario_config_2.delete_comparator("dn_config_3")


def test_scenario_config_with_env_variable_value():
    pipeline1_config = Config.configure_pipeline("pipeline1", [])
    pipeline2_config = Config.configure_pipeline("pipeline2", [])
    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        Config.configure_scenario("scenario_name", [pipeline1_config, pipeline2_config], prop="ENV[FOO]")
        assert Config.scenarios["scenario_name"].prop == "bar"
        assert Config.scenarios["scenario_name"].properties["prop"] == "bar"
        assert Config.scenarios["scenario_name"]._properties["prop"] == "ENV[FOO]"


def test_scenario_create_from_task_config():
    data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
    data_node_2_config = Config.configure_data_node(
        id="d2", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_3_config = Config.configure_data_node(
        id="d3", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    task_config_1 = Config.configure_task("t1", print, data_node_1_config, data_node_2_config, scope=Scope.GLOBAL)
    task_config_2 = Config.configure_task("t2", print, data_node_2_config, data_node_3_config, scope=Scope.GLOBAL)
    scenario_config_1 = Config.configure_scenario_from_tasks("s1", task_configs=[task_config_1, task_config_2])

    assert len(scenario_config_1.pipeline_configs) == 1
    assert len(scenario_config_1.pipeline_configs[0].task_configs) == 2
    # Should create a default pipeline name
    assert isinstance(scenario_config_1.pipeline_configs[0].id, str)
    assert scenario_config_1.pipeline_configs[0].id == f"{scenario_config_1.id}_pipeline"

    pipeline_name = "p1"
    scenario_config_2 = Config.configure_scenario_from_tasks(
        "s2", task_configs=[task_config_1, task_config_2], pipeline_id=pipeline_name
    )
    assert scenario_config_2.pipeline_configs[0].id == pipeline_name


def test_clean_config():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    scenario1_config = Config.configure_scenario_from_tasks(
        "id1", [task1_config, task2_config], Frequency.YEARLY, {"foo": "bar"}, prop="foo"
    )
    scenario2_config = Config.configure_scenario_from_tasks(
        "id2", [task2_config, task1_config], Frequency.MONTHLY, {"foz": "baz"}, prop="bar"
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
    assert scenario1_config.pipelines == scenario1_config.pipelines == []
    assert scenario1_config.frequency is scenario1_config.frequency is None
    assert scenario1_config.comparators == scenario1_config.comparators == {}
    assert scenario1_config.properties == scenario1_config.properties == {}


def test_pipeline_config_configure_deprecated():
    pipeline_config = Config.configure_default_pipeline([])
    scenario_config = Config.configure_scenario("scenario_id", pipeline_configs=[pipeline_config])
    with pytest.warns(DeprecationWarning):
        scenario_config.pipelines
    with pytest.warns(DeprecationWarning):
        scenario_config.pipeline_configs
