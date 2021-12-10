import pytest

from taipy.config import Config
from taipy.config.scenario import ScenarioConfigs
from taipy.cycle.frequency import Frequency
from taipy.exceptions.scenario import NonExistingComparator


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config.scenario_configs = ScenarioConfigs()


def my_func():
    pass


def test_scenario_creation():
    scenario = Config.scenario_configs.create(
        "scenarios1", ["pipeline1", "pipeline2"], Frequency.DAILY, comparators={"ds_config": my_func}
    )

    assert list(Config.scenario_configs) == [scenario]

    scenario2 = Config.scenario_configs.create("scenarios2", ["pipeline1", "pipeline2"], Frequency.MONTHLY)
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


def test_scenario_get_set_and_remove_comparators():
    scenario_name_1 = "scenarios1"
    ds_config_1 = "ds_config_1"
    scenario_config_1 = Config.scenario_configs.create(
        scenario_name_1, ["pipeline1", "pipeline2"], comparators={ds_config_1: my_func}
    )

    assert scenario_config_1.comparators is not None
    assert scenario_config_1.comparators[ds_config_1] == my_func
    assert len(scenario_config_1.comparators.keys()) == 1

    ds_config_2 = "ds_config_2"
    scenario_config_1.set_comparator(ds_config_2, my_func)
    assert len(scenario_config_1.comparators.keys()) == 2

    scenario_config_1.delete_comparator(ds_config_1)
    assert len(scenario_config_1.comparators.keys()) == 1

    scenario_config_1.delete_comparator(ds_config_2)
    assert len(scenario_config_1.comparators.keys()) == 0

    scenario_name_2 = "scenarios2"

    scenario_config_2 = Config.scenario_configs.create(scenario_name_2, ["pipeline1", "pipeline2"])

    assert scenario_config_2.comparators is None

    scenario_config_2.set_comparator(ds_config_1, my_func)
    assert len(scenario_config_2.comparators.keys()) == 1

    with pytest.raises(NonExistingComparator):
        scenario_config_2.delete_comparator("ds_config_3")
