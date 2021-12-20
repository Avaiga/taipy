import pytest

from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.cycle.frequency import Frequency
from taipy.exceptions.scenario import NonExistingComparator


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_config = _Config()
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
        "scenarios1", [pipeline1_config, pipeline2_config], comparators={"ds_cfg": [my_func]}
    )

    assert list(Config.scenarios()) == ["default", scenario.name]

    scenario2 = Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config], Frequency.MONTHLY)
    assert list(Config.scenarios()) == ["default", scenario.name, scenario2.name]


def test_scenario_count():
    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios()) == 2

    Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios()) == 3

    Config.add_scenario("scenarios3", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios()) == 4


def test_scenario_getitem():
    scenario_name = "scenarios1"
    scenario = Config.add_scenario(scenario_name, [pipeline1_config, pipeline2_config])

    assert Config.scenarios()[scenario_name].name == scenario.name
    assert Config.scenarios()[scenario_name].pipelines == scenario.pipelines
    assert Config.scenarios()[scenario_name].properties == scenario.properties


def test_scenario_creation_no_duplication():
    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])

    assert len(Config.scenarios()) == 2

    Config.add_scenario("scenarios1", [pipeline1_config, pipeline2_config])
    assert len(Config.scenarios()) == 2


def test_scenario_get_set_and_remove_comparators():
    ds_config_1 = "ds_config_1"
    scenario_config_1 = Config.add_scenario(
        "scenarios1", [pipeline1_config, pipeline2_config], comparators={ds_config_1: my_func}
    )

    assert scenario_config_1.comparators is not None
    assert scenario_config_1.comparators[ds_config_1] == [my_func]
    assert len(scenario_config_1.comparators.keys()) == 1

    ds_config_2 = "ds_config_2"
    scenario_config_1.add_comparator(ds_config_2, my_func)
    assert len(scenario_config_1.comparators.keys()) == 2

    scenario_config_1.delete_comparator(ds_config_1)
    assert len(scenario_config_1.comparators.keys()) == 1

    scenario_config_1.delete_comparator(ds_config_2)
    assert len(scenario_config_1.comparators.keys()) == 0

    scenario_config_2 = Config.add_scenario("scenarios2", [pipeline1_config, pipeline2_config])

    assert scenario_config_2.comparators is not None

    scenario_config_2.add_comparator(ds_config_1, my_func)
    assert len(scenario_config_2.comparators.keys()) == 1

    with pytest.raises(NonExistingComparator):
        scenario_config_2.delete_comparator("ds_config_3")
