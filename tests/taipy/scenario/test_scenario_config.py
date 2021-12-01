from taipy.config.config import Config
from taipy.config.data_source import DataSourceConfig
from taipy.config.pipeline import PipelineConfig
from taipy.config.task import TaskConfig
from taipy.data.scope import Scope
from taipy.scenario.manager import ScenarioManager


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_get_set_data():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSourceConfig("foo", "in_memory", Scope.PIPELINE, default_data=1)
    ds_2 = DataSourceConfig("bar", "in_memory", Scope.SCENARIO, default_data=0)
    ds_6 = DataSourceConfig("baz", "in_memory", Scope.PIPELINE, default_data=0)
    ds_4 = DataSourceConfig("qux", "in_memory", Scope.PIPELINE, default_data=0)

    task_mult_by_2 = TaskConfig("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = TaskConfig("mult by 3", [ds_2], mult_by_3, ds_6)
    task_mult_by_4 = TaskConfig("mult by 4", [ds_1], mult_by_4, ds_4)
    pipeline_1 = PipelineConfig("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6
    pipeline_2 = PipelineConfig("by 4", [task_mult_by_4])
    # ds_1 ---> mult by 4 ---> ds_4
    scenario = Config.scenario_configs.create("Awesome scenario", [pipeline_1, pipeline_2])

    scenario_entity = scenario_manager.create(scenario)

    assert scenario_entity.foo.read() == 1
    assert scenario_entity.bar.read() == 0
    assert scenario_entity.baz.read() == 0
    assert scenario_entity.qux.read() == 0

    scenario_manager.submit(scenario_entity.id)
    assert scenario_entity.foo.read() == 1
    assert scenario_entity.bar.read() == 2
    assert scenario_entity.baz.read() == 6
    assert scenario_entity.qux.read() == 4

    scenario_entity.foo.write("new data value")
    assert scenario_entity.foo.read() == "new data value"
    assert scenario_entity.bar.read() == 2
    assert scenario_entity.baz.read() == 6
    assert scenario_entity.qux.read() == 4

    scenario_entity.baz.write(158)
    assert scenario_entity.foo.read() == "new data value"
    assert scenario_entity.bar.read() == 2
    assert scenario_entity.baz.read() == 158
    assert scenario_entity.qux.read() == 4
