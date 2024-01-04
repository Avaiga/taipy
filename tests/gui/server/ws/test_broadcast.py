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


def test_broadcast(gui: Gui, helpers):
    # Bind test variables
    selected_val = ["value1", "value2"]  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test",
        Markdown("<|{selected_val}|selector|multiple|>"),
    )
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    sid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={sid}")
    gui._broadcast("broadcast_name", "broadcast_value")
    received_messages = ws_client.get_received()
    assert len(received_messages)
    helpers.assert_outward_simple_ws_message(received_messages[0], "U", "_bc_broadcast_name", "broadcast_value")
