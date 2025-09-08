# Copyright 2021-2025 Avaiga Private Limited
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

from taipy.gui import Gui, Markdown


@pytest.mark.skip_if_not_server("flask")
def test_ru_selector(gui: Gui, helpers, csvdata):
    # Bind test variables
    selected_val = ["value1", "value2"]  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test",
        Markdown("<|{selected_val}|selector|multiple|>"),
    )
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_server_instance())
    sid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={sid}")
    ws_client.emit(
        "message",
        {"client_id": sid, "type": "RU", "name": "", "payload": {"names": ["_TpLv_tpec_TpExPr_selected_val_TPMDL_0"]}},
    )
    # assert for received message (message that would be sent to the front-end client)
    received_messages = ws_client.get_received()
    assert len(received_messages)
    helpers.assert_outward_ws_message(
        received_messages[0], "MU", "_TpLv_tpec_TpExPr_selected_val_TPMDL_0", ["value1", "value2"]
    )


@pytest.mark.skip_if_not_server("fastapi")
@pytest.mark.teste2e
def test_ru_selector_fastapi(gui: Gui, helpers, csvdata):
    # Bind test variables
    selected_val = ["value1", "value2"]  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test",
        Markdown("<|{selected_val}|selector|multiple|>"),
    )
    helpers.run_e2e_multi_client(gui)
    ws_client = helpers.get_socketio_test_client()
    sid = helpers.create_scope_and_get_sid(gui)
    gui._server.request.set_sid(ws_client.get_sid())
    ws_client.get(f"/{Gui._JSX_URL}/test?client_id={sid}")
    ws_client.emit(
        "message",
        {"client_id": sid, "type": "RU", "name": "", "payload": {"names": ["_TpLv_tpec_TpExPr_selected_val_TPMDL_0"]}},
    )
    # assert for received message (message that would be sent to the front-end client)
    received_messages = ws_client.get_received()
    try:
        assert len(received_messages)
        helpers.assert_outward_ws_message(
            received_messages[0], "MU", "_TpLv_tpec_TpExPr_selected_val_TPMDL_0", ["value1", "value2"]
        )
    finally:
        ws_client.disconnect()
