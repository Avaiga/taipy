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

import inspect
from unittest.mock import patch

import pytest

from taipy.gui import Gui
from taipy.gui.extension import Element, ElementLibrary


class MyLibrary(ElementLibrary):
    def get_name(self) -> str:
        return "taipy_extension_example"

    def get_elements(self):
        return dict()


def test_extension_no_config(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    with pytest.warns(UserWarning):
        ret = flask_client.get("/taipy-extension/toto/titi")
        assert ret.status_code == 404


def test_extension_config_wrong_path(gui: Gui, helpers):
    Gui.add_library(MyLibrary())
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    with pytest.warns(UserWarning):
        ret = flask_client.get("/taipy-extension/taipy_extension_example/titi")
        assert ret.status_code == 404
