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

import os
import pathlib
from importlib import util

from taipy.gui import Gui


def test_image_url_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("content", "some_url")
    md_string = "<|{content}|image|>"
    expected_list = [
        "<Image",
        "content={_TpCi_tpec_TpExPr_content_TPMDL_0}",
        'defaultContent="some_url"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_image_file_md(gui: Gui, test_client, helpers):
    with open((pathlib.Path(__file__).parent.parent / "resources" / "fred.png").resolve(), "rb") as content:
        gui._bind_var_val("content", content.read())
        md_string = "<|{content}|image|>"
        expected_list = [
            "<Image",
            'defaultContent="data:image/png;base64,',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_md(gui, md_string, expected_list)


def test_image_path_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("content", str((pathlib.Path(__file__).parent.parent / "resources" / "fred.png").resolve()))
    md_string = "<|{content}|image|>"
    expected_list = [
        "<Image",
        'defaultContent="/taipy-content/taipyStatic0/fred.png',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_image_bad_file_md(gui: Gui, test_client, helpers):
    with open(os.path.abspath(__file__), "rb") as content:
        gui._bind_var_val("content", content.read())
        md_string = "<|{content}|image|>"
        expected_list = [
            "<Image",
            'defaultContent="Invalid content: text/x',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_md(gui, md_string, expected_list)


def test_image_url_html(gui: Gui, test_client, helpers):
    gui._bind_var_val("content", "some_url")
    html_string = '<taipy:image content="{content}" on_action="action" />'
    expected_list = [
        "<Image",
        'defaultContent="some_url"',
        'onAction="action"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
