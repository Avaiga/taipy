import pytest
import pandas as pd
from taipy.gui import Gui

from .helpers import Helpers

csv = pd.read_csv("current-covid-patients-hospital.csv", parse_dates=["Day"])


@pytest.fixture(scope="function")
def csvdata():
    yield csv


@pytest.fixture(scope="function")
def gui(helpers):
    yield Gui(__name__)
    # Delete Gui instance and state of some classes after each test
    helpers.test_cleanup()


@pytest.fixture
def helpers():
    return Helpers
