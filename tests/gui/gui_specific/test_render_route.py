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
import warnings
from unittest.mock import patch

from taipy.gui import Gui


def test_render_route(gui: Gui):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page("page1", "# first page")
    gui.add_page("page2", "# second page")
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    with warnings.catch_warnings(record=True):
        client = gui._server.test_client()
        response = client.get("/taipy-init")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert isinstance(response_data["locations"], dict)
        assert "/page1" in response_data["locations"]
        assert "/page2" in response_data["locations"]
        assert "/" in response_data["locations"]
        assert response_data["locations"] == {"/": "/TaiPy_root_page", "/page1": "/page1", "/page2": "/page2"}
