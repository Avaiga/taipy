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
import warnings
from unittest.mock import patch

from taipy.gui import Gui, Markdown, State, navigate


def test_navigate(gui: Gui, helpers):
    def navigate_to(state: State):
        navigate(state, "test")

    with warnings.catch_warnings(record=True):
        if frame := inspect.currentframe():
            gui._set_frame(frame)
        gui.add_page("test", Markdown("#This is a page"))
        with patch("sys.argv", ["prog"]):
            gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_flask())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test/?client_id={sid}")
        ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "navigate_to"})
        # assert for received message (message that would be sent to the front-end client)
        assert ws_client.get_received()


def test_navigate_to_no_route(gui: Gui, helpers):
    def navigate_to(state: State):
        navigate(state, "toto")

    with warnings.catch_warnings(record=True):
        if frame := inspect.currentframe():
            gui._set_frame(frame)
        gui.add_page("test", Markdown("#This is a page"))
        with patch("sys.argv", ["prog"]):
            gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_flask())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test/?client_id={sid}")
        ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "navigate_to"})
        # assert for received message (message that would be sent to the front-end client)
        assert not ws_client.get_received()


def test_on_navigate_to_inexistant(gui: Gui, helpers):
    def on_navigate(state: State, page: str):
        return "test2" if page == "test" else page

    with warnings.catch_warnings(record=True) as records:
        if frame := inspect.currentframe():
            gui._set_frame(frame)
        gui.add_page("test", Markdown("#This is a page"))
        with patch("sys.argv", ["prog"]):
            gui.run(run_server=False)
        client = gui._server.test_client()
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test?client_id={sid}")
        warns = helpers.get_taipy_warnings(records)
        assert len(warns) == 1
        text = warns[0].message.args[0] if isinstance(warns[0].message, Warning) else warns[0].message
        assert text == 'Cannot navigate to "test2": unknown page.'


def test_on_navigate_to_existant(gui: Gui, helpers):
    def on_navigate(state: State, page: str):
        return "test2" if page == "test1" else page

    with warnings.catch_warnings(record=True):
        if frame := inspect.currentframe():
            gui._set_frame(frame)
        gui.add_page("test1", Markdown("#This is a page test1"))
        gui.add_page("test2", Markdown("#This is a page test2"))
        with patch("sys.argv", ["prog"]):
            gui.run(run_server=False)
        client = gui._server.test_client()
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        content = client.get(f"/taipy-jsx/test1?client_id={sid}")
        assert content.status_code == 302
