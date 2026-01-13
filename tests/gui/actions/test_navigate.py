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
import warnings

import pytest

from taipy.gui import Gui, Markdown, navigate


@pytest.mark.skip_if_not_server("flask")
def test_navigate(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|hello|button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # ws client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_server_instance())  # type: ignore[arg-type]
    cid = helpers.create_scope_and_get_sid(gui)
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    with gui._server.test_request_context(f"/{Gui._JSX_URL}/test/?client_id={cid}", data={"client_id": cid}):
        gui._server.request.get_request_meta().client_id = cid
        navigate(gui._Gui__state, "test")  # type: ignore[attr-defined]

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(received_messages[0], "NA", {"to": "test"})


@pytest.mark.skip_if_not_server("fastapi")
@pytest.mark.teste2e
def test_navigate_fastapi(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|hello|button|>"))
    helpers.run_e2e_multi_client(gui)
    ws_client = helpers.get_socketio_test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    sid = ws_client.get_sid()
    ws_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    with gui.get_app_context():
        gui._server.request.set_sid(sid)
        gui._server.request.get_request_meta().client_id = cid
        navigate(gui._Gui__state, "test")  # type: ignore[attr-defined]

    try:
        received_messages = ws_client.get_received()
        helpers.assert_outward_ws_simple_message(received_messages[0], "NA", {"to": "test"})
    finally:
        ws_client.disconnect()


def test_bad_navigate(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        navigate(None, "test")  # type: ignore[arg-type]
        assert len(records) == 1
