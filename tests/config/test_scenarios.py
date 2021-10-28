import pytest

from taipy.config import Config
from taipy.config.scenario import ScenarioConfigs


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config.scenario_configs = ScenarioConfigs()


def test_scenario_creation():
    scenario = Config.scenario_configs.create("scenarios1", ["pipeline1", "pipeline2"])

    assert list(Config.scenario_configs) == [scenario]

    scenario2 = Config.scenario_configs.create("scenarios2", ["pipeline1", "pipeline2"])
    assert list(Config.scenario_configs) == [scenario, scenario2]


def test_scenario_count():
    Config.scenario_configs.create("scenarios1", ["pipeline1", "pipeline2"])
    assert len(Config.scenario_configs) == 1

    Config.scenario_configs.create("scenarios2", ["pipeline1", "pipeline2"])
    assert len(Config.scenario_configs) == 2

    Config.scenario_configs.create("scenarios3", ["pipeline1", "pipeline2"])
    assert len(Config.scenario_configs) == 3


def test_scenario_getitem():
    scenario_name = "scenarios1"
    scenario = Config.scenario_configs.create(scenario_name, ["pipeline1", "pipeline2"])

    assert Config.scenario_configs[scenario_name] == scenario


def test_scenario_creation_no_duplication():
    Config.scenario_configs.create("scenarios1", ["pipeline1", "pipeline2"])

    assert len(Config.scenario_configs) == 1

    Config.scenario_configs.create("scenarios1", ["pipeline1", "pipeline2"])
    assert len(Config.scenario_configs) == 1
