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

from flask import g

from taipy.gui import Gui, Markdown, State, invoke_callback


def test_invoke_callback(gui: Gui, helpers):
    name = "World!"  # noqa: F841
    btn_id = "button1"  # noqa: F841

    val = 1  # noqa: F841

    def user_callback(state: State):
        state.val = 10

    # set gui frame
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>\n<|{val}|>"))
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    # client id
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().app_context():
        g.client_id = cid
        invoke_callback(gui, cid, user_callback, [])
        assert gui._Gui__state.val == 10  # type: ignore[attr-defined]
