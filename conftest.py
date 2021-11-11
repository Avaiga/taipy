import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from taipy.common.alias import CycleId, ScenarioId
from taipy.cycle.cycle import Cycle
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.frequency import Frequency
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
def scenario():
    return Scenario("sc", [], {}, ScenarioId("sc_id"))


@pytest.fixture
def scenario_model(scope="function"):
    return ScenarioModel(ScenarioId("sc_id"), "sc", [], {})


@pytest.fixture
def cycle(scope="function"):
    return Cycle(
        "cc",
        Frequency.DAILY,
        {},
        creation_date=datetime.fromisoformat("2021-11-11T11:11:01.000001"),
        id=CycleId("cc_id"),
    )


@pytest.fixture
def cycle_model(scope="function"):
    return CycleModel(
        CycleId("cc_id"),
        "cc",
        Frequency.DAILY,
        {},
        creation_date="2021-11-11T11:11:01.000001",
        start_date=None,
        end_date=None,
    )
