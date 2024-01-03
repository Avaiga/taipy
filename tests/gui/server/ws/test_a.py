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

from taipy.gui import Gui, Markdown


def test_a_button_pressed(gui: Gui, helpers):
    def do_something(state, id):
        state.x = state.x + 10
        state.text = "a random text"

    x = 10  # noqa: F841
    text = "hi"  # noqa: F841
    # set gui frame
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test", Markdown("<|Do something!|button|on_action=do_something|id=my_button|> | <|{x}|> | <|{text}|>")
    )
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test?client_id={sid}")
    assert gui._bindings()._get_all_scopes()[sid].x == 10  # type: ignore
    assert gui._bindings()._get_all_scopes()[sid].text == "hi"  # type: ignore
    ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "do_something"})
    assert gui._bindings()._get_all_scopes()[sid].text == "a random text"
    assert gui._bindings()._get_all_scopes()[sid].x == 20  # type: ignore
    # assert for received message (message that would be sent to the front-end client)
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_message(received_messages[0], "MU", "x", 20)
    helpers.assert_outward_ws_message(received_messages[1], "MU", "text", "a random text")
