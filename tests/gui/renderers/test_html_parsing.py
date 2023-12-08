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
from unittest.mock import patch

from taipy.gui import Gui, Html


def test_simple_html(gui: Gui, helpers):
    # html_string = "<html><head></head><body><h1>test</h1><taipy:field value=\"test\"/></body></html>"
    html_string = "<html><head></head><body><h1>test</h1></body></html>"
    gui._set_frame(inspect.currentframe())
    gui.add_page("test", Html(html_string))
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    client = gui._server.test_client()
    jsx = client.get("/taipy-jsx/test").json["jsx"]
    assert jsx == "<h1>test</h1>"
