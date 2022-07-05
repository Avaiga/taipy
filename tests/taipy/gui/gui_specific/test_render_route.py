# Copyright 2022 Avaiga Private Limited
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

from taipy.gui import Gui


def test_render_route(gui: Gui):
    gui._set_frame(inspect.currentframe())
    gui.add_page("page1", "# first page")
    gui.add_page("page2", "# second page")
    gui.run(run_server=False)
    with warnings.catch_warnings(record=True) as w:
        client = gui._server.test_client()
        response = client.get("/taipy-init")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert "page1" in response_data["router"]
        assert "page2" in response_data["router"]
        assert "/" in response_data["router"]
        assert (
            response_data["router"]
            == '<Routes key="routes"><Route path="/" key="TaiPy_root_page" element={<MainPage key="trTaiPy_root_page" path="/TaiPy_root_page" route="/page1" />} ><Route path="page1" key="page1" element={<TaipyRendered key="trpage1"/>} /><Route path="page2" key="page2" element={<TaipyRendered key="trpage2"/>} /><Route path="*" key="NotFound" element={<NotFound404 />} /></Route></Routes>'
        )
