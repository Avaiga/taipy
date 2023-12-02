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
import sys
from importlib.util import find_spec
from pathlib import Path

import pandas as pd  # type: ignore
import pytest
from flask import Flask, g


def pytest_configure(config):
    if (find_spec("src") and find_spec("src.taipy")) and (not find_spec("taipy") or not find_spec("taipy.gui")):
        import src.taipy.gui
        import src.taipy.gui._renderers.builder
        import src.taipy.gui._warnings
        import src.taipy.gui.builder
        import src.taipy.gui.data.decimator.lttb
        import src.taipy.gui.data.decimator.minmax
        import src.taipy.gui.data.decimator.rdp
        import src.taipy.gui.data.decimator.scatter_decimator
        import src.taipy.gui.data.utils
        import src.taipy.gui.extension
        import src.taipy.gui.utils._map_dict
        import src.taipy.gui.utils._variable_directory
        import src.taipy.gui.utils.expr_var_name

        sys.modules["taipy.gui._warnings"] = sys.modules["src.taipy.gui._warnings"]
        sys.modules["taipy.gui._renderers.builder"] = sys.modules["src.taipy.gui._renderers.builder"]
        sys.modules["taipy.gui.utils._variable_directory"] = sys.modules["src.taipy.gui.utils._variable_directory"]
        sys.modules["taipy.gui.utils.expr_var_name"] = sys.modules["src.taipy.gui.utils.expr_var_name"]
        sys.modules["taipy.gui.utils._map_dict"] = sys.modules["src.taipy.gui.utils._map_dict"]
        sys.modules["taipy.gui.extension"] = sys.modules["src.taipy.gui.extension"]
        sys.modules["taipy.gui.data.utils"] = sys.modules["src.taipy.gui.data.utils"]
        sys.modules["taipy.gui.data.decimator.lttb"] = sys.modules["src.taipy.gui.data.decimator.lttb"]
        sys.modules["taipy.gui.data.decimator.rdp"] = sys.modules["src.taipy.gui.data.decimator.rdp"]
        sys.modules["taipy.gui.data.decimator.minmax"] = sys.modules["src.taipy.gui.data.decimator.minmax"]
        sys.modules["taipy.gui.data.decimator.scatter_decimator"] = sys.modules[
            "src.taipy.gui.data.decimator.scatter_decimator"
        ]
        sys.modules["taipy.gui"] = sys.modules["src.taipy.gui"]
        sys.modules["taipy.gui.builder"] = sys.modules["src.taipy.gui.builder"]


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
