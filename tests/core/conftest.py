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
import pickle
import shutil
from datetime import datetime
from queue import Queue
from unittest.mock import patch

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import close_all_sessions

from taipy.common.config import Config
from taipy.common.config.checker._checker import _Checker
from taipy.common.config.common.frequency import Frequency
from taipy.common.config.common.scope import Scope
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core._version._version import _Version
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.config import (
    _ConfigIdChecker,
    _CoreSectionChecker,
    _DataNodeConfigChecker,
    _JobConfigChecker,
    _ScenarioConfigChecker,
    _TaskConfigChecker,
)
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.cycle._cycle_model import _CycleModel
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_id import CycleId
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data._data_model import _DataNodeModel
from taipy.core.data.in_memory import DataNodeId, InMemoryDataNode
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.job.job_id import JobId
from taipy.core.notification.notifier import Notifier
from taipy.core.orchestrator import Orchestrator
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario._scenario_model import _ScenarioModel
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_id import ScenarioId
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.sequence.sequence import Sequence
from taipy.core.sequence.sequence_id import SequenceId
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission import Submission
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task, TaskId

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
def excel_file_with_sheet_name(tmpdir_factory) -> str:
    excel = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")
    excel.to_excel(str(fn), sheet_name="sheet_name", index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def json_file(tmpdir_factory) -> str:
    json_data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.json")
    json_data.to_json(str(fn), orient="records")
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file_with_multi_sheet(tmpdir_factory) -> str:
    excel_multi_sheet = {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")

    with pd.ExcelWriter(str(fn)) as writer:
        for key in excel_multi_sheet.keys():
            excel_multi_sheet[key].to_excel(writer, key, index=False)

    return fn.strpath


@pytest.fixture(scope="function")
def pickle_file_path(tmpdir_factory) -> str:
    data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.p")
    with open(str(fn), "wb") as f:
        pickle.dump(data, f)
    return fn.strpath


@pytest.fixture(scope="function")
def parquet_file_path(tmpdir_factory) -> str:
    data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.parquet")
    data.to_parquet(str(fn))
    return fn.strpath


@pytest.fixture(scope="function")
def tmp_sqlite_db_file_path(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data")
    db_name = "df"
    file_extension = ".db"
    db = create_engine("sqlite:///" + os.path.join(fn.strpath, f"{db_name}{file_extension}"))
    conn = db.connect()
    conn.execute(text("CREATE TABLE example (foo int, bar int);"))
    conn.execute(text("INSERT INTO example (foo, bar) VALUES (1, 2);"))
    conn.execute(text("INSERT INTO example (foo, bar) VALUES (3, 4);"))
    conn.commit()
    conn.close()
    db.dispose()

    return fn.strpath, db_name, file_extension


@pytest.fixture(scope="function")
def tmp_sqlite_sqlite3_file_path(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data")
    db_name = "df"
    file_extension = ".sqlite3"

    db = create_engine("sqlite:///" + os.path.join(fn.strpath, f"{db_name}{file_extension}"))
    conn = db.connect()
    conn.execute(text("CREATE TABLE example (foo int, bar int);"))
    conn.execute(text("INSERT INTO example (foo, bar) VALUES (1, 2);"))
    conn.execute(text("INSERT INTO example (foo, bar) VALUES (3, 4);"))
    conn.commit()
    conn.close()
    db.dispose()

    return fn.strpath, db_name, file_extension


@pytest.fixture(scope="function")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(scope="function")
def default_multi_sheet_data_frame():
    return {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }


@pytest.fixture(scope="function")
def current_datetime():
    return current_time


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario(
        "sc",
        set(),
        {},
        set(),
        ScenarioId("SCENARIO_scenario_id"),
        current_time,
        is_primary=False,
        tags={"foo"},
        version="random_version_number",
        cycle=None,
    )


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode(
        "data_node_config_id", Scope.SCENARIO, version="random_version_number", id=DataNodeId("DATANODE_data_node_id")
    )


@pytest.fixture(scope="function")
def data_node_model():
    return _DataNodeModel(
        "my_dn_id",
        "test_data_node",
        Scope.SCENARIO,
        "csv",
        "name",
        "owner_id",
        list({"parent_id_1", "parent_id_2"}),
        datetime(1985, 10, 14, 2, 30, 0).isoformat(),
        [{"timestamp": datetime(1985, 10, 14, 2, 30, 0).isoformat(), "job_id": "job_id"}],
        "latest",
        None,
        None,
        False,
        {"path": "/path", "has_header": True, "prop": "ENV[FOO]", "exposed_type": "pandas"},
    )


@pytest.fixture(scope="function")
def task(data_node):
    dn = InMemoryDataNode("dn_config_id", Scope.SCENARIO, version="random_version_number")
    return Task("task_config_id", {}, print, [data_node], [dn], TaskId("TASK_task_id"))


@pytest.fixture(scope="function")
def scenario_model(cycle):
    return _ScenarioModel(
        ScenarioId("sc_id"),
        "sc",
        set(),
        set(),
        {},
        creation_date=current_time.isoformat(),
        primary_scenario=False,
        subscribers=[],
        tags=["foo"],
        version="random_version_number",
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
        id=CycleId("CYCLE_cycle_id"),
    )


@pytest.fixture(scope="class")
def sequence():
    return Sequence(
        {},
        [],
        SequenceId("sequence_id"),
        owner_id="owner_id",
        parent_ids={"parent_id_1", "parent_id_2"},
        version="random_version_number",
    )


@pytest.fixture(scope="function")
def job(task):
    return Job(JobId("job"), task, "foo", "bar", version="random_version_number")


@pytest.fixture(scope="function")
def submission(task):
    return Submission(task.id, task._ID_PREFIX, task.config_id, properties={})


@pytest.fixture(scope="function")
def _version():
    return _Version(id="foo", config=Config._applied_config)


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


@pytest.fixture(scope="function")
def tmp_sqlite(tmpdir_factory):
    fn = tmpdir_factory.mktemp("db")
    return os.path.join(fn.strpath, "test.db")


@pytest.fixture(scope="session", autouse=True)
def cleanup_files():
    for path in [".data", ".my_data", "user_data", ".taipy"]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

    yield

    for path in [".data", ".my_data", "user_data", ".taipy"]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="function", autouse=True)
def clean_repository(init_config, init_managers, init_orchestrator, init_notifier, clean_argparser):
    clean_argparser()
    close_all_sessions()
    init_config()
    init_orchestrator()
    init_managers()
    init_config()
    init_notifier()

    with patch("sys.argv", ["prog"]):
        yield

    clean_argparser()
    close_all_sessions()
    init_orchestrator()
    init_managers()
    init_config()
    init_notifier()


@pytest.fixture
def init_config(reset_configuration_singleton, inject_core_sections):
    def _init_config():
        reset_configuration_singleton()
        inject_core_sections()

        _Checker.add_checker(_ConfigIdChecker)
        _Checker.add_checker(_CoreSectionChecker)
        _Checker.add_checker(_DataNodeConfigChecker)
        _Checker.add_checker(_JobConfigChecker)
        _Checker.add_checker(_TaskConfigChecker)
        _Checker.add_checker(_ScenarioConfigChecker)

        Config.configure_core(read_entity_retry=0)
        Orchestrator._is_running = False
        Orchestrator._version_is_initialized = False

    return _init_config


@pytest.fixture
def init_managers():
    def _init_managers():
        _CycleManagerFactory._build_manager()._delete_all()
        _ScenarioManagerFactory._build_manager()._delete_all()
        _SequenceManagerFactory._build_manager()._delete_all()
        _JobManagerFactory._build_manager()._delete_all()
        _TaskManagerFactory._build_manager()._delete_all()
        _DataManagerFactory._build_manager()._delete_all()
        _VersionManagerFactory._build_manager()._delete_all()
        _SubmissionManagerFactory._build_manager()._delete_all()

    return _init_managers


@pytest.fixture
def init_orchestrator():
    def _init_orchestrator():
        _OrchestratorFactory._remove_dispatcher()

        if _OrchestratorFactory._orchestrator is None:
            _OrchestratorFactory._build_orchestrator()
        _OrchestratorFactory._build_dispatcher(force_restart=True)
        _OrchestratorFactory._orchestrator.jobs_to_run = Queue()
        _OrchestratorFactory._orchestrator.blocked_jobs = []

    return _init_orchestrator


@pytest.fixture
def init_notifier():
    def _init_notifier():
        Notifier._topics_registrations_list = {}

    return _init_notifier


@pytest.fixture
def sql_engine():
    return create_engine("sqlite:///:memory:")
