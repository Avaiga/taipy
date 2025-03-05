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

from flask import g

from taipy.gui import Gui, Markdown, close_notification, notify


def test_notify(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())  # type: ignore[arg-type]
    cid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        id = notify(gui._Gui__state, "Info", "Message", id="id")  # type: ignore[attr-defined]
        assert id == "id"
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(
        received_messages[0], "AL", {"nType": "Info", "message": "Message", "notificationId": "id"}
    )


def test_bad_notify(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        id = notify(None, "Info", "Message", id="id")  # type: ignore[arg-type]
        assert id is None
        assert len(records) == 1


def test_close_notification(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())  # type: ignore[arg-type]
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        id = notify(gui._Gui__state, "Info", "Message", id="id")  # type: ignore[attr-defined]
        close_notification(gui._Gui__state, id)  # type: ignore[attr-defined, arg-type]
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(
        received_messages[0], "AL", {"nType": "Info", "message": "Message", "notificationId": "id"}
    )
    helpers.assert_outward_ws_simple_message(received_messages[1], "AL", {"nType": "", "notificationId": "id"})


def test_bad_close_notification(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        close_notification(None, "id")  # type: ignore[arg-type]
        assert len(records) == 1
