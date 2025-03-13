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
import typing as t
import warnings

from flask import Flask, g

from taipy.gui import Gui, Markdown, State, download


def test_download(gui: Gui, helpers):
    def on_download_action(state: State):
        pass

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(t.cast(Flask, gui._server.get_flask()))
    cid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        download(gui._Gui__state, "some text", "filename.txt", "on_download_action")  # type: ignore[attr-defined]

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(
        received_messages[0], "DF", {"name": "filename.txt", "onAction": "on_download_action"}
    )


def test_download_fn(gui: Gui, helpers):
    def on_download_action(state: State):
        pass

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(t.cast(Flask, gui._server.get_flask()))
    cid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        download(gui._Gui__state, "some text", "filename.txt", on_download_action)  # type: ignore[attr-defined]

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_simple_message(
        received_messages[0],
        "DF",
        {"name": "filename.txt", "context": "test_download"},
    )
    assert "onAction" in received_messages[0]["args"] # inner function is treated as lambda


def test_bad_download(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        download(None, "some text", "filename.txt", "on_download_action")  # type: ignore[arg-type]
        assert len(records) == 1
