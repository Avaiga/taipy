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

import inspect

import pytest

from taipy.gui import Gui


def test_user_content_without_callback(gui: Gui, helpers):
    gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    with pytest.warns(UserWarning):
        ret = flask_client.get(gui._get_user_content_url("path"))
        assert ret.status_code == 404


def test_user_content_with_wrong_callback(gui: Gui, helpers):
    def on_user_content_cb(state, path, arguments):
        return None

    on_user_content = on_user_content_cb  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    with pytest.warns(UserWarning):
        ret = flask_client.get(gui._get_user_content_url("path", {"a": "b"}))
        assert ret.status_code == 404


def test_user_content_with_callback(gui: Gui, helpers):
    def on_user_content_cb(state, path, arguments):
        return ""

    on_user_content = on_user_content_cb  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    ret = flask_client.get(gui._get_user_content_url("path"))
    assert ret.status_code == 200
