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
from unittest.mock import patch

from flask import g

from taipy.gui import Gui, Markdown, hold_control


def test_hold_control(gui: Gui, helpers):
    name = "World!"  # noqa: F841
    btn_id = "button1"  # noqa: F841

    # set gui frame
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>"))
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        hold_control(gui._Gui__state)  # type: ignore[attr-defined]

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(
        received_messages[0], "BL", {"action": "_taipy_on_cancel_block_ui", "message": "Work in Progress..."}
    )
