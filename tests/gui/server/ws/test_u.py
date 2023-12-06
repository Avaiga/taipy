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

from taipy.gui import Gui, Markdown


def ws_u_assert_template(gui: Gui, helpers, value_before_update, value_after_update, payload):
    # Bind test variable
    var = value_before_update  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    # Bind a page so that the variable will be evaluated as expression
    gui.add_page("test", Markdown("<|{var}|>"))
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test?client_id={sid}")
    assert gui._bindings()._get_all_scopes()[sid].var == value_before_update
    ws_client.emit("message", {"client_id": sid, "type": "U", "name": "tpec_TpExPr_var_TPMDL_0", "payload": payload})
    assert gui._bindings()._get_all_scopes()[sid].var == value_after_update
    # assert for received message (message that would be sent to the front-end client)
    received_message = ws_client.get_received()
    assert len(received_message)
    helpers.assert_outward_ws_message(received_message[0], "MU", "tpec_TpExPr_var_TPMDL_0", value_after_update)


def test_ws_u_string(gui: Gui, helpers):
    value_before_update = "a random string"
    value_after_update = "a random string is added"
    payload = {"value": value_after_update}

    # set gui frame
    gui._set_frame(inspect.currentframe())

    ws_u_assert_template(gui, helpers, value_before_update, value_after_update, payload)


def test_ws_u_number(gui: Gui, helpers):
    value_before_update = 10
    value_after_update = "11"
    payload = {"value": value_after_update}

    # set gui frame
    gui._set_frame(inspect.currentframe())

    ws_u_assert_template(gui, helpers, value_before_update, value_after_update, payload)
