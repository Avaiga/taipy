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

from taipy.gui import Gui


def test_get_status(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    ret = flask_client.get("/taipy.status.json")
    assert ret.status_code == 200, f"status_code => {ret.status_code} != 200"
    assert ret.mimetype == "application/json", f"mimetype => {ret.mimetype} != application/json"
    assert ret.json, "json is not defined"
    assert "gui" in ret.json, "json has no key gui"
    gui = ret.json.get("gui")
    assert isinstance(gui, dict), "json.gui is not a dict"
    assert "user_status" in gui, "json.gui has no key user_status"
    assert gui.get("user_status") == "", "json.gui.user_status is not empty"


def test_get_extended_status(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, extended_status=True)
    flask_client = gui._server.test_client()
    ret = flask_client.get("/taipy.status.json")
    assert ret.status_code == 200, f"status_code => {ret.status_code} != 200"
    assert ret.mimetype == "application/json", f"mimetype => {ret.mimetype} != application/json"
    assert ret.json, "json is not defined"
    gui_ret = ret.json.get("gui")
    assert "backend_version" in gui_ret, "json.gui has no key backend_version"
    assert "flask_version" in gui_ret, "json.gui has no key flask_version"
    assert "frontend_version" in gui_ret, "json.gui has no key frontend_version"
    assert "host" in gui_ret, "json.gui has no key host"
    assert "python_version" in gui_ret, "json.gui has no key python_version"
    assert "user_status" in gui_ret, "json.gui has no key user_status"
    assert gui_ret.get("user_status") == "", "json.gui.user_status is not empty"


def test_get_status_with_user_status(gui: Gui):
    user_status = "user_status"

    def on_status(state):
        return user_status

    if frame := inspect.currentframe():
        gui._set_frame(frame)

    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    ret = flask_client.get("/taipy.status.json")
    assert ret.status_code == 200, f"status_code => {ret.status_code} != 200"
    assert ret.json, "json is not defined"
    gui_ret = ret.json.get("gui")
    assert "user_status" in gui_ret, "json.gui has no key user_status"
    assert gui_ret.get("user_status") == user_status
    assert f'json.gui.user_status => {gui_ret.get("user_status")} != {user_status}'
