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
import json

from taipy.gui import Gui, Markdown


def test_actions(gui: Gui, helpers):
    def an_action(state):
        pass

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|action button|button|on_action={an_action}|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    response = flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    assert response.status_code == 200, f"response.status_code {response.status_code} != 200"
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert isinstance(response_data, dict), "response_data is not Dict"
    assert "jsx" in response_data, "jsx not in response_data"
    jsx = response_data["jsx"]
    function_name = ""
    for part in jsx.split(" "):
        if part.startswith("onAction="):
            function_name = part.split('"')[1]
            break
    assert function_name
    scope = gui._bindings()._get_all_scopes().get(cid)
    assert getattr(scope, function_name) is an_action
