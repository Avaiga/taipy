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

from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core._version._version_manager_factory import _VersionManagerFactory
from src.taipy.core._version._version_repository_factory import _VersionRepositoryFactory
from src.taipy.core.common.alias import CycleId, PipelineId, ScenarioId
from src.taipy.core.config import (
    DataNodeConfig,
    JobConfig,
    PipelineConfig,
    ScenarioConfig,
    TaskConfig,
    _DataNodeConfigChecker,
    _JobConfigChecker,
    _PipelineConfigChecker,
    _ScenarioConfigChecker,
    _TaskConfigChecker,
)
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.cycle._cycle_model import _CycleModel
from src.taipy.core.cycle._cycle_repository_factory import _CycleRepositoryFactory
from src.taipy.core.cycle.cycle import Cycle
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data._data_repository_factory import _DataRepositoryFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.job._job_repository_factory import _JobRepositoryFactory
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline._pipeline_model import _PipelineModel
from src.taipy.core.pipeline._pipeline_repository_factory import _PipelineRepositoryFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario._scenario_model import _ScenarioModel
from src.taipy.core.scenario._scenario_repository_factory import _ScenarioRepositoryFactory
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task._task_repository_factory import _TaskRepositoryFactory
from src.taipy.core.task.task import Task
from taipy.config._config import _Config
from taipy.config._toml_serializer import _TomlSerializer
from taipy.config.checker._checker import _Checker
from taipy.config.checker._checkers._gLobal_config_checker import _GlobalConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config

current_time = datetime.now()
_SchedulerFactory._build_scheduler()


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
def json_file(tmpdir_factory) -> str:
    json = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.json")
    json.to_json(str(fn))
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
def parquet_file_path(tmpdir_factory) -> str:
    data = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.parquet")
    data.to_parquet(str(fn))
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


@pytest.fixture(scope="session", autouse=True)
def cleanup_files():
    if os.path.exists("None"):
        os.remove("None")

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
        [],
        {},
        ScenarioId("sc_id"),
        current_time,
        is_primary=False,
        tags={"foo"},
        version="random_version_number",
        cycle=None,
    )


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode("data_node_config_id", Scope.PIPELINE, version="random_version_number")


@pytest.fixture(scope="function")
def task(data_node):
    dn = InMemoryDataNode("dn_config_id", Scope.PIPELINE, version="random_version_number")
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
def pipeline():
    return Pipeline(
        "pipeline",
        {},
        [],
        PipelineId("pipeline_id"),
        owner_id="owner_id",
        parent_ids=set(["parent_id_1", "parent_id_2"]),
        version="random_version_number",
    )


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
    return _PipelineModel(
        PipelineId("pipeline_id"),
        "owner_id",
        list({"parent_id_1", "parent_id_2"}),
        "pipeline",
        {},
        [],
        [],
        "random_version_number",
    )


@pytest.fixture(scope="function")
def tmp_sqlite(tmpdir_factory):
    fn = tmpdir_factory.mktemp("db")
    return os.path.join(fn.strpath, "test.db")


@pytest.fixture(scope="function", autouse=True)
def clean_repository():
    if Config.global_config.repository_type == "sql":
        close_sql_database_session_connection()
        init_managers()
    init_config()
    init_scheduler()
    init_managers()
    init_config()

    yield

    if Config.global_config.repository_type == "sql":
        close_sql_database_session_connection()
        init_managers()
    init_config()
    init_scheduler()
    init_managers()
    init_config()


def close_sql_database_session_connection():
    _ScenarioRepositoryFactory._build_repository().repo.session.close_all()
    _PipelineRepositoryFactory._build_repository().repo.session.close_all()
    _DataRepositoryFactory._build_repository().repo.session.close_all()
    _TaskRepositoryFactory._build_repository().repo.session.close_all()
    _JobRepositoryFactory._build_repository().repo.session.close_all()
    _CycleRepositoryFactory._build_repository().repo.session.close_all()


def init_config():
    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()
    _Checker._checkers = [_GlobalConfigChecker]

    from src.taipy.core.config import _inject_section

    _inject_section(
        JobConfig, "job_config", JobConfig("development"), [("configure_job_executions", JobConfig._configure)]
    )
    _inject_section(
        DataNodeConfig,
        "data_nodes",
        DataNodeConfig.default_config(),
        [
            ("configure_data_node", DataNodeConfig._configure),
            ("configure_default_data_node", DataNodeConfig._configure_default),
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
        [("configure_task", TaskConfig._configure), ("configure_default_task", TaskConfig._configure_default)],
    )
    _inject_section(
        PipelineConfig,
        "pipelines",
        PipelineConfig.default_config(),
        [
            ("configure_pipeline", PipelineConfig._configure),
            ("configure_default_pipeline", PipelineConfig._configure_default),
        ],
    )
    _inject_section(
        ScenarioConfig,
        "scenarios",
        ScenarioConfig.default_config(),
        [
            ("configure_scenario", ScenarioConfig._configure),
            ("configure_default_scenario", ScenarioConfig._configure_default),
            ("configure_scenario_from_tasks", ScenarioConfig._configure_from_tasks),
        ],
    )
    _Checker.add_checker(_JobConfigChecker)
    _Checker.add_checker(_DataNodeConfigChecker)
    _Checker.add_checker(_TaskConfigChecker)
    _Checker.add_checker(_PipelineConfigChecker)
    _Checker.add_checker(_ScenarioConfigChecker)


def init_managers():
    _CycleManagerFactory._build_manager()._delete_all()
    _ScenarioManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()
    _VersionManagerFactory._build_manager()._delete_all()


def init_scheduler():
    if _SchedulerFactory._scheduler is None:
        _SchedulerFactory._build_scheduler()
    _SchedulerFactory._build_dispatcher()
    _SchedulerFactory._scheduler.jobs_to_run = Queue()
    _SchedulerFactory._scheduler.blocked_jobs = []


def check_repositories_are(repo_type="default"):
    cycle_repository = _CycleRepositoryFactory._build_repository()
    expected_cycle_repository = _CycleRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(cycle_repository) != type(expected_cycle_repository):
        return False

    scenario_repository = _ScenarioRepositoryFactory._build_repository()
    expected_scenario_repository = _ScenarioRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(scenario_repository) != type(expected_scenario_repository):
        return False

    pipeline_repository = _PipelineRepositoryFactory._build_repository()
    expected_pipeline_repository = _PipelineRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(pipeline_repository) != type(expected_pipeline_repository):
        return False

    task_repository = _TaskRepositoryFactory._build_repository()
    expected_task_repository = _TaskRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(task_repository) != type(expected_task_repository):
        return False

    job_repository = _JobRepositoryFactory._build_repository()
    expected_job_repository = _JobRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(job_repository) != type(expected_job_repository):
        return False

    data_repository = _DataRepositoryFactory._build_repository()
    expected_data_repository = _DataRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(data_repository) != type(expected_data_repository):
        return False

    version_repository = _VersionRepositoryFactory._build_repository()
    expected_version_repository = _VersionRepositoryFactory._REPOSITORY_MAP.get(repo_type)()
    if type(version_repository) != type(expected_version_repository):
        return False

    return True


def check_repositories_are_empty():
    cycle_repository = _CycleRepositoryFactory._build_repository()
    cycles = cycle_repository._load_all()
    if len(cycles) != 0:
        return False

    scenario_repository = _ScenarioRepositoryFactory._build_repository()
    scenarios = scenario_repository._load_all()
    if len(scenarios) != 0:
        return False

    pipeline_repository = _PipelineRepositoryFactory._build_repository()
    pipelines = pipeline_repository._load_all()
    if len(pipelines) != 0:
        return False

    task_repository = _TaskRepositoryFactory._build_repository()
    tasks = task_repository._load_all()
    if len(tasks) != 0:
        return False

    job_repository = _JobRepositoryFactory._build_repository()
    jobs = job_repository._load_all()
    if len(jobs) != 0:
        return False

    data_repository = _DataRepositoryFactory._build_repository()
    data_nodes = data_repository._load_all()
    if len(data_nodes) != 0:
        return False

    version_repository = _VersionRepositoryFactory._build_repository()
    version = version_repository._load_all()
    if len(version) != 0:
        return False

    return True
