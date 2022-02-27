import os
from unittest import mock

import pytest

from taipy.core.common.frequency import Frequency
from taipy.core.config._config import _Config
from taipy.core.config.config import Config
from taipy.core.data.scope import Scope
from taipy.core.exceptions.scenario import NonExistingComparator
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario_manager import ScenarioManager


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config.default_config()


pipeline1_config = Config.add_pipeline(
    "pipeline1",
    [],
)
pipeline2_config = Config.add_pipeline("pipeline2", [])


def my_func():
    pass


def test_scenario_creation():
    scenario = Config.add_scenario(
        "scenarios1", [pipeline1_config, pipeline2_config], comparators={"dn_cfg": [my_func]}
    )

    assert list(Config.scenarios) == ["default", scenario.name]

    scenario2 = Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config], Frequency.MONTHLY)
    assert list(Config.scenarios) == ["default", scenario.name, scenario2.name]


def test_scenario_count():
    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 2

    Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 3

    Config.add_scenario("scenarios3", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 4


def test_scenario_getitem():
    scenario_name = "scenarios1"
    scenario = Config.add_scenario(scenario_name, [pipeline1_config, pipeline2_config])

    assert Config.scenarios[scenario_name].name == scenario.name
    assert Config.scenarios[scenario_name].pipelines == scenario.pipelines
    assert Config.scenarios[scenario_name].properties == scenario.properties


def test_scenario_creation_no_duplication():
    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])

    assert len(Config.scenarios) == 2

    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios) == 2


def test_scenario_get_set_and_remove_comparators():
    dn_config_1 = "dn_config_1"
    scenario_config_1 = Config.add_scenario(
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

    scenario_config_2 = Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config])

    assert scenario_config_2.comparators is not None

    scenario_config_2.add_comparator(dn_config_1, my_func)
    assert len(scenario_config_2.comparators.keys()) == 1

    with pytest.raises(NonExistingComparator):
        scenario_config_2.delete_comparator("dn_config_3")


def test_scenario_config_with_env_variable_value():
    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        Config.add_scenario("scenario_name", [pipeline1_config, pipeline2_config], prop="ENV[FOO]")
        assert Config.scenarios["scenario_name"].prop == "bar"


def test_scenario_create_from_tasks():
    data_node_1_config = Config.add_data_node(name="d1", storage_type="in_memory", scope=Scope.SCENARIO)
    data_node_2_config = Config.add_data_node(
        name="d2", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_3_config = Config.add_data_node(
        name="d3", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    task_config_1 = Config.add_task("t1", print, data_node_1_config, data_node_2_config, scope=Scope.GLOBAL)
    task_config_2 = Config.add_task("t2", print, data_node_2_config, data_node_3_config, scope=Scope.GLOBAL)
    scenario_config_1 = Config.add_scenario_from_tasks("s1", task_configs=[task_config_1, task_config_2])
    ScenarioManager.submit(ScenarioManager.create(scenario_config_1))
    assert len(ScenarioManager.get_all()) == 1
    assert len(PipelineManager.get_all()) == 1
    assert len(scenario_config_1.pipelines) == 1
    assert len(scenario_config_1.pipelines[0].tasks) == 2
    # Should create a default pipeline name
    assert isinstance(scenario_config_1.pipelines[0].name, str)
    assert scenario_config_1.pipelines[0].name == f"{scenario_config_1.name}_pipeline"

    pipeline_name = "p1"
    scenario_config_2 = Config.add_scenario_from_tasks(
        "s2", task_configs=[task_config_1, task_config_2], pipeline_name=pipeline_name
    )
    ScenarioManager.submit(ScenarioManager.create(scenario_config_2))
    assert len(ScenarioManager.get_all()) == 2
    assert len(PipelineManager.get_all()) == 2
    assert scenario_config_2.pipelines[0].name == pipeline_name
