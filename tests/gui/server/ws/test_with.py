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
from taipy.gui.data.data_scope import _DataScopes


def test_sending_messages_in_group(gui: Gui, helpers):
    name = "World!"  # noqa: F841
    btn_id = "button1"  # noqa: F841

    # set gui frame
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>"))
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    cid = _DataScopes._GLOBAL_ID
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    assert gui._bindings()._get_all_scopes()[cid].name == "World!"  # type: ignore
    assert gui._bindings()._get_all_scopes()[cid].btn_id == "button1"  # type: ignore

    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        with gui as aGui:
            aGui._Gui__state.name = "Monde!"
            aGui._Gui__state.btn_id = "button2"

    assert gui._bindings()._get_all_scopes()[cid].name == "Monde!"
    assert gui._bindings()._get_all_scopes()[cid].btn_id == "button2"  # type: ignore

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_multiple_message(received_messages[0], "MS", 2)
