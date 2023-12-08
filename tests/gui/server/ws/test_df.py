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
import logging
import pathlib
from unittest.mock import patch

import pytest

from taipy.gui import Gui, download


def test_download_file(gui: Gui, helpers):
    def do_something(state, id):
        download(state, (pathlib.Path(__file__).parent.parent.parent / "resources" / "taipan.jpg"))

    # Bind a page so that the function will be called
    # gui.add_page(
    #     "test", Markdown("<|Do something!|button|on_action=do_something|id=my_button|>")
    # )
    # set gui frame
    gui._set_frame(inspect.currentframe())

    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ws_client.emit("message", {"client_id": sid, "type": "A", "name": "my_button", "payload": "do_something"})
    # assert for received message (message that would be sent to the front-end client)
    received_messages = ws_client.get_received()
    assert len(received_messages) == 1
    assert isinstance(received_messages[0], dict)
    assert "name" in received_messages[0] and received_messages[0]["name"] == "message"
    assert "args" in received_messages[0]
    args = received_messages[0]["args"]
    assert "type" in args and args["type"] == "DF"
    assert "content" in args and args["content"] == "/taipy-content/taipyStatic0/taipan.jpg"
    logging.getLogger().debug(args["content"])
