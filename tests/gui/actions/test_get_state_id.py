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

from taipy.gui import Gui, Markdown, get_state_id


def test_get_state_id(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    with gui.get_app_context():
        gui._server.request.get_request_meta().client_id = cid
        assert cid == get_state_id(gui._Gui__state)  # type: ignore[attr-defined]


def test_bad_get_state_id(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        assert get_state_id(None) is None  # type: ignore[arg-type]
        assert len(records) == 0
