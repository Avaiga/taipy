import pytest

from taipy.config.config import Config
from taipy.cycle.frequency import Frequency
from taipy.data import Scope
from taipy.exceptions.configuration import LoadingError
from tests.taipy.config.named_temporary_file import NamedTemporaryFile


def test_read_error_node_can_not_appear_twice():
    config = NamedTemporaryFile(
        """
[JOB]
parallel_execution = false
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
parallel_execution = true
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
remote_execution = false
parallel_execution = true
nb_of_workers = 1
hostname = "localhost"
airflow_dag_folder = ".dag/"
airflow_folder = ".airflow/"

[DATA_SOURCE.default]
storage_type = "in_memory"
scope = "PIPELINE"
custom = "default_custom_prop"

[DATA_SOURCE.ds1]
storage_type = "pickle"
scope = "PIPELINE"
custom = "custom property"
default_data = "ds1"

[DATA_SOURCE.ds2]
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
    Config.set_job_config(mode="standalone", parallel_execution=True)
    Config.add_default_data_source(storage_type="in_memory", custom="default_custom_prop")
    ds1_cfg_v2 = Config.add_data_source("ds1", storage_type="pickle", default_data="ds1", custom="custom property")
    ds2_cfg_v2 = Config.add_data_source(
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
