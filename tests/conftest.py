# Copyright 2022 Avaiga Private Limited
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
import pickle
import shutil
from datetime import datetime
from queue import Queue

import pandas as pd
import pytest
from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope
from taipy.config.scenario.frequency import Frequency

from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.common.alias import CycleId, PipelineId, ScenarioId
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.cycle._cycle_model import _CycleModel
from src.taipy.core.cycle.cycle import Cycle
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline._pipeline_model import _PipelineModel
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario._scenario_model import _ScenarioModel
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task

current_time = datetime.now()


@pytest.fixture(scope="function")
def csv_file(tmpdir_factory) -> str:
    csv = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.csv")
    csv.to_csv(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file(tmpdir_factory) -> str:
    excel = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")
    excel.to_excel(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file_with_multi_sheet(tmpdir_factory) -> str:
    excel_multi_sheet = {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")

    writer = pd.ExcelWriter(str(fn))
    for key in excel_multi_sheet.keys():
        excel_multi_sheet[key].to_excel(writer, key, index=False)
    writer.save()

    return fn.strpath


@pytest.fixture(scope="function")
def pickle_file_path(tmpdir_factory) -> str:
    data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.p")
    pickle.dump(data, open(str(fn), "wb"))
    return fn.strpath


@pytest.fixture(scope="function")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(scope="function")
def default_multi_sheet_data_frame():
    return {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }


@pytest.fixture(autouse=True)
def cleanup_files():
    from time import sleep

    sleep(0.1)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)


@pytest.fixture(scope="function")
def current_datetime():
    return current_time


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario("sc", [], {}, ScenarioId("sc_id"), current_time, is_primary=False, tags={"foo"}, cycle=None)


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode("data_node_config_id", Scope.PIPELINE)


@pytest.fixture(scope="function")
def task(data_node):
    dn = InMemoryDataNode("dn_config_id", Scope.PIPELINE)
    return Task("task_config_id", print, [data_node], [dn])


@pytest.fixture(scope="function")
def scenario_model(cycle):
    return _ScenarioModel(
        ScenarioId("sc_id"),
        "sc",
        [],
        {},
        creation_date=current_time.isoformat(),
        primary_scenario=False,
        subscribers=[],
        tags=["foo"],
        cycle=None,
    )


@pytest.fixture(scope="function")
def cycle():
    example_date = datetime.fromisoformat("2021-11-11T11:11:01.000001")
    return Cycle(
        Frequency.DAILY,
        {},
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
        name="cc",
        id=CycleId("cc_id"),
    )


@pytest.fixture(scope="class")
def pipeline():
    return Pipeline("pipeline", {}, [], PipelineId("pipeline_id"))


@pytest.fixture(scope="function")
def cycle_model():
    return _CycleModel(
        CycleId("cc_id"),
        "cc",
        Frequency.DAILY,
        {},
        creation_date="2021-11-11T11:11:01.000001",
        start_date="2021-11-11T11:11:01.000001",
        end_date="2021-11-11T11:11:01.000001",
    )


@pytest.fixture(scope="class")
def pipeline_model():
    return _PipelineModel(PipelineId("pipeline_id"), None, "pipeline", {}, [], [])


@pytest.fixture(scope="function", autouse=True)
def setup():
    delete_everything()


def delete_everything():
    _Scheduler._update_job_config()
    _Scheduler.jobs_to_run = Queue()
    _Scheduler.blocked_jobs = []
    _TaskManager._scheduler = _SchedulerFactory._build_scheduler
    _ScenarioManager._delete_all()
    _PipelineManager._delete_all()
    _DataManager._delete_all()
    _TaskManager._delete_all()
    _JobManager._delete_all()
    _CycleManager._delete_all()

    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()


@pytest.fixture(scope="function", autouse=True)
def teardown():
    delete_everything()
