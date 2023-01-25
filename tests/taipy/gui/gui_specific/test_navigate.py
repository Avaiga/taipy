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
import json
import warnings

from taipy.gui import Gui, Markdown, State, navigate


def test_navigate(gui: Gui, helpers):
    def navigate_to(state: State):
        navigate(state, "test")

    with warnings.catch_warnings(record=True):
        gui._set_frame(inspect.currentframe())
        gui.add_page("test", Markdown("#This is a page"))
        gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_flask())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test/?client_id={sid}")
        ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "navigate_to"})
        # assert for received message (message that would be sent to the frontend client)
        assert ws_client.get_received()


def test_navigate_to_no_route(gui: Gui, helpers):
    def navigate_to(state: State):
        navigate(state, "toto")

    with warnings.catch_warnings(record=True):
        gui._set_frame(inspect.currentframe())
        gui.add_page("test", Markdown("#This is a page"))
        gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_flask())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test/?client_id={sid}")
        ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "navigate_to"})
        # assert for received message (message that would be sent to the frontend client)
        assert not ws_client.get_received()
