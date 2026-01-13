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

from taipy.gui import Gui, Markdown


@pytest.mark.skip_if_not_server("flask")
def test_favicon(gui: Gui, helpers):
    with warnings.catch_warnings(record=True):
        gui._set_frame(inspect.currentframe())
        gui.add_page("test", Markdown("#This is a page"))
        gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_server_instance())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/{Gui._JSX_URL}/test/?client_id={sid}")
        gui.set_favicon("https://newfavicon.com/favicon.png")
        # assert for received message (message that would be sent to the front-end client)
        msgs = ws_client.get_received()
        assert msgs is not None
        assert msgs[0].get("args", {}).get("type", None) == "FV"
        assert msgs[0].get("args", {}).get("payload", {}).get("value", None) == "https://newfavicon.com/favicon.png"


@pytest.mark.skip_if_not_server("fastapi")
@pytest.mark.teste2e
def test_favicon_fastapi(gui: Gui, helpers):
    with warnings.catch_warnings(record=True):
        gui._set_frame(inspect.currentframe())
        gui.add_page("test", Markdown("#This is a page"))
        helpers.run_e2e_multi_client(gui)
        ws_client = helpers.get_socketio_test_client()
        sid = helpers.create_scope_and_get_sid(gui)
        gui._server.request.set_sid(ws_client.get_sid())
        ws_client.get(f"/{Gui._JSX_URL}/test?client_id={sid}")
        gui.set_favicon("https://newfavicon.com/favicon.png")
        msgs = ws_client.get_received()
        try:
            assert len(msgs) > 0
            assert msgs[0].get("args", {}).get("type", None) == "FV"
            assert msgs[0].get("args", {}).get("payload", {}).get("value", None) == "https://newfavicon.com/favicon.png"
        finally:
            ws_client.disconnect()
