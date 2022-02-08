import os
import shutil
import uuid
from datetime import datetime, timedelta

import pandas as pd
import pytest
from dotenv import load_dotenv
from taipy.common.alias import DataNodeId, JobId
from taipy.common.frequency import Frequency
from taipy.config import Config
from taipy.cycle import Cycle
from taipy.cycle.manager import CycleManager
from taipy.data import InMemoryDataNode, Scope
from taipy.job import Job, JobManager
from taipy.pipeline import Pipeline
from taipy.scenario import Scenario
from taipy.task import Task
from taipy.task.manager import TaskManager

from taipy_rest.app import create_app


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    return app


@pytest.fixture
def datanode_data():
    return {
        "name": "foo",
        "storage_type": "in_memory",
        "scope": "pipeline",
        "default_data": ["1991-01-01T00:00:00"],
    }


@pytest.fixture
def task_data():
    return {
        "config_name": "foo",
        "input_ids": ["DATASOURCE_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
        "function_name": "print",
        "function_module": "builtins",
        "output_ids": ["DATASOURCE_foo_4d9923b8-eb9f-4f3c-8055-3a1ce8bee309"],
    }


@pytest.fixture
def pipeline_data():
    return {
        "name": "foo",
        "task_ids": ["TASK_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
    }


@pytest.fixture
def scenario_data():
    return {
        "name": "foo",
        "pipeline_ids": ["PIPELINE_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
        "properties": {},
    }


@pytest.fixture
def default_datanode():
    return InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("foo"),
        "my name",
        "parent_id",
        properties={"default_data": [1, 2, 3, 4, 5, 6]},
    )


@pytest.fixture
def default_df_datanode():
    return InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio2"),
        "my name",
        "parent_id",
        properties={
            "default_data": pd.DataFrame(
                [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}]
            )
        },
    )


@pytest.fixture
def default_datanode_config():
    return Config.add_data_node(uuid.uuid4().hex, "in_memory", Scope.PIPELINE)


@pytest.fixture
def default_datanode_config_list():
    configs = []
    for i in range(10):
        configs.append(
            Config.add_data_node(
                name=f"ds-{i}", storage_type="in_memory", scope=Scope.PIPELINE
            )
        )
    return configs


def __default_task():
    input_ds = InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio"),
        "my name",
        "parent_id",
        properties={"default_data": "In memory Data Source"},
    )

    output_ds = InMemoryDataNode(
        "output_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio"),
        "my name",
        "parent_id",
        properties={"default_data": "In memory Data Source"},
    )
    return Task(
        "foo",
        [input_ds],
        print,
        [output_ds],
        None,
    )


@pytest.fixture
def default_task():
    return __default_task()


@pytest.fixture
def default_task_config():
    return Config.add_task("task1", [], print, [])


@pytest.fixture
def default_task_config_list():
    configs = []
    for i in range(10):
        configs.append(Config.add_task(f"task-{i}", [], print, []))
    return configs


def __default_pipeline():
    return Pipeline(
        config_name="foo",
        properties={},
        tasks=[__default_task()],
    )


def __task_config():
    return Config.add_task("task1", [], print, [])


@pytest.fixture
def default_pipeline():
    return __default_pipeline()


@pytest.fixture
def default_pipeline_config():
    return Config.add_pipeline(uuid.uuid4().hex, __task_config())


@pytest.fixture
def default_pipeline_config_list():
    configs = []
    for i in range(10):
        configs.append(Config.add_pipeline(uuid.uuid4().hex, __task_config()))
    return configs


@pytest.fixture
def default_scenario_config():
    return Config.add_scenario(
        uuid.uuid4().hex, [Config.add_pipeline(uuid.uuid4().hex, __task_config())]
    )


@pytest.fixture
def default_scenario_config_list():
    configs = []
    for i in range(10):
        configs.append(
            Config.add_scenario(
                uuid.uuid4().hex,
                [Config.add_pipeline(uuid.uuid4().hex, __task_config())],
            )
        )
    return configs


@pytest.fixture
def default_scenario():
    return Scenario(
        config_name="foo",
        properties={},
        pipelines=[__default_pipeline()],
    )


def __create_cycle(name="foo"):
    now = datetime.now()
    return Cycle(
        name=name,
        frequency=Frequency.DAILY,
        properties={},
        creation_date=now,
        start_date=now,
        end_date=now + timedelta(days=5),
    )


@pytest.fixture
def create_cycle_list():
    cycles = []
    manager = CycleManager()
    for i in range(10):
        c = __create_cycle(f"cycle-{1}")
        manager.set(c)
    return cycles


@pytest.fixture
def cycle_data():
    return {
        "name": "foo",
        "frequency": "daily",
        "properties": {},
        "creation_date": "2022-02-03T22:17:27.317114",
        "start_date": "2022-02-03T22:17:27.317114",
        "end_date": "2022-02-08T22:17:27.317114",
    }


@pytest.fixture
def default_cycle():
    return __create_cycle()


def __create_job():
    task_manager = TaskManager()
    task = __default_task()
    task_manager.set(task)
    return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task)


@pytest.fixture
def default_job():
    return __create_job()


@pytest.fixture
def create_job_list():
    jobs = []
    manager = JobManager()
    for i in range(10):
        c = __create_job()
        manager.set(c)
    return jobs


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")
