# Copyright 2021-2024 Avaiga Private Limited
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
import shutil
import uuid
from datetime import datetime, timedelta

import pandas as pd
import pytest
from dotenv import load_dotenv

from taipy.config import Config
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.core import Cycle, DataNodeId, Job, JobId, Scenario, Sequence, Task
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.job._job_manager import _JobManager
from taipy.core.task._task_manager import _TaskManager
from taipy.rest.app import create_app

from .setup.shared.algorithms import evaluate, forecast


@pytest.fixture
def setup_end_to_end():
    model_cfg = Config.configure_data_node("model", path="setup/my_model.p", storage_type="pickle")

    day_cfg = Config.configure_data_node(id="day")
    forecasts_cfg = Config.configure_data_node(id="forecasts")
    forecast_task_cfg = Config.configure_task(
        id="forecast_task",
        input=[model_cfg, day_cfg],
        function=forecast,
        output=forecasts_cfg,
    )

    historical_temperature_cfg = Config.configure_data_node(
        "historical_temperature",
        storage_type="csv",
        path="setup/historical_temperature.csv",
        has_header=True,
    )
    evaluation_cfg = Config.configure_data_node("evaluation")
    evaluate_task_cfg = Config.configure_task(
        "evaluate_task",
        input=[historical_temperature_cfg, forecasts_cfg, day_cfg],
        function=evaluate,
        output=evaluation_cfg,
    )

    scenario_config = Config.configure_scenario(
        "scenario", [forecast_task_cfg, evaluate_task_cfg], frequency=Frequency.DAILY
    )
    scenario_config.add_sequences({"sequence": [forecast_task_cfg, evaluate_task_cfg]})


@pytest.fixture()
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    with app.app_context(), app.test_request_context():
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def datanode_data():
    return {
        "name": "foo",
        "storage_type": "in_memory",
        "scope": "scenario",
        "default_data": ["1991-01-01T00:00:00"],
    }


@pytest.fixture
def task_data():
    return {
        "config_id": "foo",
        "input_ids": ["DATASOURCE_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
        "function_name": "print",
        "function_module": "builtins",
        "output_ids": ["DATASOURCE_foo_4d9923b8-eb9f-4f3c-8055-3a1ce8bee309"],
    }


@pytest.fixture
def sequence_data():
    return {
        "name": "foo",
        "task_ids": ["TASK_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
    }


@pytest.fixture
def scenario_data():
    return {
        "name": "foo",
        "sequence_ids": ["SEQUENCE_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
        "properties": {},
    }


@pytest.fixture
def default_datanode():
    return InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("f"),
        "my name",
        "owner_id",
        properties={"default_data": [1, 2, 3, 4, 5, 6]},
    )


@pytest.fixture
def default_df_datanode():
    return InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio2"),
        "my name",
        "owner_id",
        properties={"default_data": pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}])},
    )


@pytest.fixture
def default_datanode_config():
    return Config.configure_data_node(f"taipy_{uuid.uuid4().hex}", "in_memory", Scope.SCENARIO)


@pytest.fixture
def default_datanode_config_list():
    configs = []
    for i in range(10):
        configs.append(Config.configure_data_node(id=f"ds_{i}", storage_type="in_memory", scope=Scope.SCENARIO))
    return configs


def __default_task():
    input_ds = InMemoryDataNode(
        "input_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio"),
        "my name",
        "owner_id",
        properties={"default_data": "In memory Data Source"},
    )

    output_ds = InMemoryDataNode(
        "output_ds",
        Scope.SCENARIO,
        DataNodeId("id_uio"),
        "my name",
        "owner_id",
        properties={"default_data": "In memory Data Source"},
    )
    return Task(
        config_id="foo",
        properties={},
        function=print,
        input=[input_ds],
        output=[output_ds],
        id=None,
    )


@pytest.fixture
def default_task():
    return __default_task()


@pytest.fixture
def default_task_config():
    return Config.configure_task("task1", print, [], [])


@pytest.fixture
def default_task_config_list():
    configs = []
    for i in range(10):
        configs.append(Config.configure_task(f"task_{i}", print, [], []))
    return configs


def __default_sequence():
    return Sequence(properties={"name": "foo"}, tasks=[__default_task()], sequence_id="SEQUENCE_foo_SCENARIO_acb")


def __task_config():
    return Config.configure_task("task1", print, [], [])


@pytest.fixture
def default_sequence():
    return __default_sequence()


@pytest.fixture
def default_scenario_config():
    task_config = __task_config()
    scenario_config = Config.configure_scenario(
        f"taipy_{uuid.uuid4().hex}",
        [task_config],
    )
    scenario_config.add_sequences({"sequence": [task_config]})
    return scenario_config


@pytest.fixture
def default_scenario_config_list():
    configs = []
    for _ in range(10):
        task_config = Config.configure_task(f"taipy_{uuid.uuid4().hex}", print)
        scenario_config = Config.configure_scenario(
            f"taipy_{uuid.uuid4().hex}",
            [task_config],
        )
        scenario_config.add_sequences({"sequence": [task_config]})
        configs.append(scenario_config)
    return configs


@pytest.fixture
def default_scenario():
    return Scenario(config_id="foo", properties={}, tasks=[__default_task()], scenario_id="SCENARIO_scenario_id")


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
    manager = _CycleManager
    for i in range(10):
        c = __create_cycle(f"cycle_{i}")
        manager._set(c)
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
    task_manager = _TaskManager
    task = __default_task()
    task_manager._set(task)
    submit_id = f"SUBMISSION_{str(uuid.uuid4())}"
    return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task, submit_id=submit_id, submit_entity_id=task.id)


@pytest.fixture
def default_job():
    return __create_job()


@pytest.fixture
def create_job_list():
    jobs = []
    manager = _JobManager
    for i in range(10):
        c = __create_job()
        manager._set(c)
    return jobs


@pytest.fixture(scope="function", autouse=True)
def cleanup_files(reset_configuration_singleton, inject_core_sections):
    reset_configuration_singleton()
    inject_core_sections()

    Config.configure_core(repository_type="filesystem")
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists(".my_data"):
        shutil.rmtree(".my_data", ignore_errors=True)
