import pytest

from taipy.common.frequency import Frequency
from taipy.config.config import Config
from taipy.data import Scope
from taipy.exceptions.configuration import LoadingError
from tests.taipy.config.named_temporary_file import NamedTemporaryFile


def test_read_error_node_can_not_appear_twice():
    config = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 40

[JOB]
parallel_execution = true
nb_of_workers = 10
    """
    )

    with pytest.raises(LoadingError, match="Can not load configuration"):
        Config.load(config.filename)


def test_read_skip_configuration_outside_nodes():
    config = NamedTemporaryFile(
        """
nb_of_workers = 10
    """
    )

    Config.load(config.filename)

    assert not Config.job_config().parallel_execution
    assert Config.job_config().nb_of_workers == 1


def test_write_configuration_file():
    expected_config = """
[TAIPY]
notification = true
broker_endpoint = "my_broker_end_point"
root_folder = "./taipy/"
storage_folder = ".data/"

[JOB]
mode = "standalone"
nb_of_workers = 1
hostname = "localhost:8080"
airflow_dags_folder = ".dags/"
airflow_folder = ".airflow/"
start_airflow = false
airflow_api_retry = 10
airflow_user = "admin"

[DATA_NODE.default]
storage_type = "in_memory"
scope = "PIPELINE"
custom = "default_custom_prop"

[DATA_NODE.ds1]
storage_type = "pickle"
scope = "PIPELINE"
custom = "custom property"
default_data = "ds1"

[DATA_NODE.ds2]
storage_type = "in_memory"
scope = "SCENARIO"
custom = "default_custom_prop"
foo = "bar"
default_data = "ds2"

[TASK.default]
inputs = []
outputs = []

[TASK.t1]
inputs = [ "ds1",]
function = "<built-in function print>"
outputs = [ "ds2",]
description = "t1 description"

[PIPELINE.default]
tasks = []

[PIPELINE.p1]
tasks = [ "t1",]
cron = "daily"

[SCENARIO.default]
pipelines = []
frequency = "QUARTERLY"
owner = "Michel Platini"

[SCENARIO.s1]
pipelines = [ "p1",]
frequency = "QUARTERLY"
owner = "Raymond Kopa"
    """.strip()

    Config.set_global_config(True, "my_broker_end_point")
    Config.set_job_config(mode="standalone")
    Config.add_default_data_node(storage_type="in_memory", custom="default_custom_prop")
    ds1_cfg_v2 = Config.add_data_node("ds1", storage_type="pickle", default_data="ds1", custom="custom property")
    ds2_cfg_v2 = Config.add_data_node(
        "ds2", storage_type="in_memory", scope=Scope.SCENARIO, foo="bar", default_data="ds2"
    )
    t1_cfg_v2 = Config.add_task("t1", ds1_cfg_v2, print, ds2_cfg_v2, description="t1 description")
    p1_cfg_v2 = Config.add_pipeline("p1", t1_cfg_v2, cron="daily")
    Config.add_default_scenario([], Frequency.QUARTERLY, owner="Michel Platini")
    Config.add_scenario("s1", p1_cfg_v2, frequency=Frequency.QUARTERLY, owner="Raymond Kopa")
    tf = NamedTemporaryFile()
    Config.export(tf.filename)
    actual_config = tf.read().strip()

    assert actual_config == expected_config


def test_all_entities_use_protected_name():
    file_config = NamedTemporaryFile(
        """
        [DATA_NODE.default]
        has_header = true

        [DATA_NODE.my_dataNode]
        path = "/data/csv"

        [DATA_NODE.my_dataNode2]
        path = "/data2/csv"

        [TASK.my_Task]
        inputs = ["my_dataNode"]
        outputs = ["my_dataNode2"]
        description = "task description"

        [PIPELINE.my_Pipeline]
        tasks = [ "my_Task",]
        cron = "daily"

        [SCENARIO.my_Scenario]
        pipelines = [ "my_Pipeline",]
        owner = "John Doe"
        """
    )
    Config.load(file_config.filename)
    data_node_1_config = Config.add_data_node(name="my_datanode")
    data_node_2_config = Config.add_data_node(name="my_datanode2")
    task_config = Config.add_task("my_task", data_node_1_config, print, data_node_2_config)
    pipeline_config = Config.add_pipeline("my_pipeline", task_config)
    Config.add_scenario("my_scenario", pipeline_config)

    assert len(Config.data_nodes()) == 3
    assert Config.data_nodes()["my_datanode"].path == "/data/csv"
    assert Config.data_nodes()["my_datanode2"].path == "/data2/csv"
    assert Config.data_nodes()["my_datanode"].name == "my_datanode"
    assert Config.data_nodes()["my_datanode2"].name == "my_datanode2"

    assert len(Config.tasks()) == 2
    assert Config.tasks()["my_task"].name == "my_task"
    assert Config.tasks()["my_task"].description == "task description"

    assert len(Config.pipelines()) == 2
    assert Config.pipelines()["my_pipeline"].name == "my_pipeline"
    assert Config.pipelines()["my_pipeline"].cron == "daily"

    assert len(Config.scenarios()) == 2
    assert Config.scenarios()["my_scenario"].name == "my_scenario"
    assert Config.scenarios()["my_scenario"].owner == "John Doe"
