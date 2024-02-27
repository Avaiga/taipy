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

import json
import warnings
from types import SimpleNamespace

from taipy.gui import Gui, Markdown


def test_partial(gui: Gui):
    with warnings.catch_warnings(record=True):
        gui.add_partial(Markdown("#This is a partial"))
        gui.run(run_server=False)
        client = gui._server.test_client()
        response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert "jsx" in response_data and "This is a partial" in response_data["jsx"]


def test_partial_update(gui: Gui):
    with warnings.catch_warnings(record=True):
        partial = gui.add_partial(Markdown("#This is a partial"))
        gui.run(run_server=False, single_client=True)
        client = gui._server.test_client()
        response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert "jsx" in response_data and "This is a partial" in response_data["jsx"]
        # update partial
        fake_state = SimpleNamespace()
        fake_state._gui = gui
        partial.update_content(fake_state, "#partial updated")  # type: ignore
        response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert "jsx" in response_data and "partial updated" in response_data["jsx"]
