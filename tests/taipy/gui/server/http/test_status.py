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

import inspect
from flask import g
import pytest

from src.taipy.gui import Gui


def test_get_status(gui: Gui):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    ret = flask_client.get("/status.json")
    assert ret.status_code == 200, f"status_code => {ret.status_code} != 200"
    assert ret.mimetype == "application/json", f"mimetype => {ret.mimetype} != application/json"
    assert ret.json, "json is not defined"
    assert "backend_version" in ret.json, f"json has no key backend_version"
    assert "flask_version" in ret.json, f"json has no key flask_version"
    assert "frontend_version" in ret.json, f"json has no key frontend_version"
    assert "host" in ret.json, f"json has no key host"
    assert "python_version" in ret.json, f"json has no key python_version"
    assert "user_status" in ret.json, f"json has no key user_status"
    assert ret.json.get("user_status") == "", f"json.user_status is not empty"

def test_get_status_with_user_status(gui: Gui):
    user_status = "user_status"
    def on_status(state):
        return user_status 

    gui._set_frame(inspect.currentframe())

    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    ret = flask_client.get("/status.json")
    assert ret.status_code == 200, f"status_code => {ret.status_code} != 200"
    assert ret.json, "json is not defined"
    assert "user_status" in ret.json, f"json has no key user_status"
    assert ret.json.get("user_status") == user_status, f'json.user_status => {ret.json.get("user_status")} != {user_status}'
