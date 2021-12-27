import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from taipy.common.alias import CycleId, Dag, PipelineId, ScenarioId
from taipy.common.frequency import Frequency
from taipy.cycle.cycle import Cycle
from taipy.cycle.cycle_model import CycleModel
from taipy.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.scenario import ScenarioManager
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel


@pytest.fixture(scope="function")
def csv_file(tmpdir_factory):
    csv = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.csv")
    csv.to_csv(str(fn), index=False)
    return fn


@pytest.fixture(scope="session")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")


@pytest.fixture(scope="function")
def current_datetime():
    return datetime.now()


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario("sc", [], {}, ScenarioId("sc_id"), is_master=False, cycle=None)


@pytest.fixture(scope="function")
def scenario_model(cycle):
    return ScenarioModel(ScenarioId("sc_id"), "sc", [], {}, master_scenario=False, subscribers=[], cycle=None)


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
    return CycleModel(
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
    return PipelineModel(PipelineId("pipeline_id"), None, "pipeline", {}, Dag({}), Dag({}), [])


@pytest.fixture(scope="function", autouse=True)
def setup():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    task_scheduler = task_manager.task_scheduler
    data_manager = scenario_manager.data_manager
    cycle_manager = scenario_manager.cycle_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()
    task_scheduler.delete_all()
    cycle_manager.delete_all()


@pytest.fixture(scope="function", autouse=True)
def teardown():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    task_scheduler = task_manager.task_scheduler
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()
    task_scheduler.delete_all()
