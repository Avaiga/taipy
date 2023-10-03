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
import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_html_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("name", "World!")
    gui._bind_var_val("btn_id", "button1")
    with tgb.Page(frame=None) as page:
        tgb.html("h1", "This is a header", style="color:Tomato;")
        with tgb.html("p", "This is a paragraph.", style="color:green;"):
            tgb.html("a", "a text", href="https://www.w3schools.com", target="_blank")
            tgb.html("br")
            tgb.html("b", "This is bold text inside the paragrah.")
    expected_list = [
        '<h1 style="color:Tomato;">This is a header',
        '<p style="color:green;">This is a paragraph.',
        '<a href="https://www.w3schools.com" target="_blank">a text',
        "<br >",
        "<b >This is bold text inside the paragrah.",
    ]
    helpers.test_control_builder(gui, page, expected_list)
