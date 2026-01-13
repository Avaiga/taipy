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

from taipy.gui import Gui, Markdown, get_user_content_url


def test_get_content_url(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello|button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # WS client and emit
    cid = helpers.create_scope_and_get_sid(gui)
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    with gui._server.test_request_context(f"/{Gui._JSX_URL}/test/?client_id={cid}", data={"client_id": cid}):
        gui._server.request.get_request_meta().client_id = cid
        url = get_user_content_url(gui._Gui__state, "path")  # type: ignore[attr-defined]
        assert url == "/taipy-user-content/path?client_id=test"


def test_bad_resume_control(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        get_user_content_url(None)  # type: ignore[arg-type]
        assert len(records) == 1
