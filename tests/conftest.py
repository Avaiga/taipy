# Copyright 2023 Avaiga Private Limited
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
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable, DropTable

from src.taipy.core._core import Core
from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core._repository._sql_repository import connection
from src.taipy.core._version._version import _Version
from src.taipy.core._version._version_manager_factory import _VersionManagerFactory
from src.taipy.core._version._version_model import _VersionModel
from src.taipy.core.config import (
    CoreSection,
    DataNodeConfig,
    JobConfig,
    MigrationConfig,
    ScenarioConfig,
    TaskConfig,
    _ConfigIdChecker,
    _CoreSectionChecker,
    _DataNodeConfigChecker,
    _JobConfigChecker,
    _ScenarioConfigChecker,
    _TaskConfigChecker,
)
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.cycle._cycle_model import _CycleModel
from src.taipy.core.cycle.cycle import Cycle
from src.taipy.core.cycle.cycle_id import CycleId
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data._data_model import _DataNodeModel
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.job._job_model import _JobModel
from src.taipy.core.job.job import Job
from src.taipy.core.job.job_id import JobId
from src.taipy.core.notification.notifier import Notifier
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario._scenario_model import _ScenarioModel
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.scenario.scenario_id import ScenarioId
from src.taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from src.taipy.core.sequence.sequence import Sequence
from src.taipy.core.sequence.sequence_id import SequenceId
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task._task_model import _TaskModel
from src.taipy.core.task.task import Task
from taipy.config import _inject_section
from taipy.config._config import _Config
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.checker._checker import _Checker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config

current_time = datetime.now()
_OrchestratorFactory._build_orchestrator()


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


@pytest.fixture(scope="session", autouse=True)
def cleanup_files():
    yield

    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists(".my_data"):
        shutil.rmtree(".my_data", ignore_errors=True)


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
        ScenarioId("sc_id"),
        current_time,
        is_primary=False,
        tags={"foo"},
        version="random_version_number",
        cycle=None,
    )


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode("data_node_config_id", Scope.SCENARIO, version="random_version_number")


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
        [dict(timestamp=datetime(1985, 10, 14, 2, 30, 0).isoformat(), job_id="job_id")],
        "latest",
        None,
        None,
        False,
        {"path": "/path", "has_header": True, "prop": "ENV[FOO]", "exposed_type": "pandas"},
    )


@pytest.fixture(scope="function")
def task(data_node):
    dn = InMemoryDataNode("dn_config_id", Scope.SCENARIO, version="random_version_number")
    return Task("task_config_id", {}, print, [data_node], [dn])


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
        id=CycleId("cc_id"),
    )


@pytest.fixture(scope="class")
def sequence():
    return Sequence(
        {},
        [],
        SequenceId("sequence_id"),
        owner_id="owner_id",
        parent_ids=set(["parent_id_1", "parent_id_2"]),
        version="random_version_number",
    )


@pytest.fixture(scope="function")
def job(task):
    return Job(JobId("job"), task, "foo", "bar", version="random_version_number")


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


@pytest.fixture(scope="function", autouse=True)
def clean_repository():
    from sqlalchemy.orm import close_all_sessions

    close_all_sessions()
    init_config()
    init_orchestrator()
    init_managers()
    init_config()
    init_notifier()

    yield


def init_config():
    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()
    _Checker._checkers = []

    _inject_section(
        JobConfig, "job_config", JobConfig("development"), [("configure_job_executions", JobConfig._configure)], True
    )
    _inject_section(
        CoreSection,
        "core",
        CoreSection.default_config(),
        [("configure_core", CoreSection._configure)],
        add_to_unconflicted_sections=True,
    )
    _inject_section(
        DataNodeConfig,
        "data_nodes",
        DataNodeConfig.default_config(),
        [
            ("configure_data_node", DataNodeConfig._configure),
            ("configure_data_node_from", DataNodeConfig._configure_from),
            ("set_default_data_node_configuration", DataNodeConfig._set_default_configuration),
            ("configure_csv_data_node", DataNodeConfig._configure_csv),
            ("configure_json_data_node", DataNodeConfig._configure_json),
            ("configure_sql_table_data_node", DataNodeConfig._configure_sql_table),
            ("configure_sql_data_node", DataNodeConfig._configure_sql),
            ("configure_mongo_collection_data_node", DataNodeConfig._configure_mongo_collection),
            ("configure_in_memory_data_node", DataNodeConfig._configure_in_memory),
            ("configure_pickle_data_node", DataNodeConfig._configure_pickle),
            ("configure_excel_data_node", DataNodeConfig._configure_excel),
            ("configure_generic_data_node", DataNodeConfig._configure_generic),
        ],
    )
    _inject_section(
        TaskConfig,
        "tasks",
        TaskConfig.default_config(),
        [
            ("configure_task", TaskConfig._configure),
            ("set_default_task_configuration", TaskConfig._set_default_configuration),
        ],
    )
    _inject_section(
        ScenarioConfig,
        "scenarios",
        ScenarioConfig.default_config(),
        [
            ("configure_scenario", ScenarioConfig._configure),
            ("set_default_scenario_configuration", ScenarioConfig._set_default_configuration),
        ],
    )
    _inject_section(
        MigrationConfig,
        "migration_functions",
        MigrationConfig.default_config(),
        [("add_migration_function", MigrationConfig._add_migration_function)],
        True,
    )
    _Checker.add_checker(_ConfigIdChecker)
    _Checker.add_checker(_CoreSectionChecker)
    _Checker.add_checker(_DataNodeConfigChecker)
    _Checker.add_checker(_JobConfigChecker)
    # We don't need to add _MigrationConfigChecker because it is run only when the Core service is run.
    _Checker.add_checker(_TaskConfigChecker)
    _Checker.add_checker(_ScenarioConfigChecker)

    Config.configure_core(read_entity_retry=0)
    Core._is_running = False


def init_managers():
    _CycleManagerFactory._build_manager()._delete_all()
    _ScenarioManagerFactory._build_manager()._delete_all()
    _SequenceManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()
    _VersionManagerFactory._build_manager()._delete_all()


def init_orchestrator():
    if _OrchestratorFactory._orchestrator is None:
        _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    _OrchestratorFactory._orchestrator.jobs_to_run = Queue()
    _OrchestratorFactory._orchestrator.blocked_jobs = []


def init_notifier():
    Notifier._topics_registrations_list = {}


@pytest.fixture
def sql_engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def init_sql_repo(tmp_sqlite):
    Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})

    # Clean SQLite database
    if connection:
        connection.execute(str(DropTable(_CycleModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(str(DropTable(_DataNodeModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(str(DropTable(_JobModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(str(DropTable(_ScenarioModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(str(DropTable(_TaskModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(str(DropTable(_VersionModel.__table__, if_exists=True).compile(dialect=sqlite.dialect())))

        connection.execute(
            str(CreateTable(_CycleModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        connection.execute(
            str(CreateTable(_DataNodeModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        connection.execute(str(CreateTable(_JobModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(
            str(CreateTable(_ScenarioModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        connection.execute(str(CreateTable(_TaskModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect())))
        connection.execute(
            str(CreateTable(_VersionModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )

    return tmp_sqlite
