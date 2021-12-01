import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from taipy.common.alias import CycleId, Dag, PipelineId, ScenarioId
from taipy.cycle.cycle import Cycle
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.frequency import Frequency
from taipy.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
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
def week_example():
    return datetime(2021, 11, 16, 0, 0, 0, 0)


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
        name="cc",
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
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
