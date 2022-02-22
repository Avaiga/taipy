import os
from pathlib import Path

import pandas as pd  # type: ignore
import pytest

from taipy.gui import Gui

from .helpers import Helpers

csv = pd.read_csv(
    f"{Path(Path(__file__).parent.resolve())}{os.path.sep}current-covid-patients-hospital.csv", parse_dates=["Day"]
)
small_dataframe_data = {"name": ["A", "B", "C"], "value": [1, 2, 3]}


@pytest.fixture(scope="function")
def csvdata():
    yield csv


@pytest.fixture(scope="function")
def small_dataframe():
    yield small_dataframe_data


@pytest.fixture(scope="function")
def gui(helpers):
    yield Gui()
    # Delete Gui instance and state of some classes after each test
    helpers.test_cleanup()


@pytest.fixture
def helpers():
    return Helpers
