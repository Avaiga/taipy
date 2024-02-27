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
from pathlib import Path
from unittest.mock import patch

import pandas as pd  # type: ignore
import pytest
from flask import Flask, g

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
    from taipy.gui import Gui

    gui = Gui()
    yield gui
    # Delete Gui instance and state of some classes after each test
    gui.stop()
    helpers.test_cleanup()


@pytest.fixture
def helpers():
    from .helpers import Helpers

    return Helpers


@pytest.fixture
def test_client():
    flask_app = Flask("Test App")

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            g.client_id = "test client id"
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="function", autouse=True)
def patch_cli_args():
    with patch("sys.argv", ["prog"]):
        yield
