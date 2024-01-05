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

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_image_url_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("content", "some_url")
    with tgb.Page(frame=None) as page:
        tgb.image(content="{content}")  # type: ignore[attr-defined]
    expected_list = [
        "<Image",
        "content={_TpCi_tpec_TpExPr_content_TPMDL_0}",
        'defaultContent="some_url"',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_image_file_builder(gui: Gui, test_client, helpers):
    with open((pathlib.Path(__file__).parent.parent.parent / "resources" / "fred.png").resolve(), "rb") as content:
        gui._bind_var_val("content", content.read())
        with tgb.Page(frame=None) as page:
            tgb.image(content="{content}")  # type: ignore[attr-defined]
        expected_list = [
            "<Image",
            'defaultContent="data:image/png;base64,',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_builder(gui, page, expected_list)


def test_image_path_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val(
        "content", str((pathlib.Path(__file__).parent.parent.parent / "resources" / "fred.png").resolve())
    )
    with tgb.Page(frame=None) as page:
        tgb.image(content="{content}")  # type: ignore[attr-defined]
    expected_list = [
        "<Image",
        'defaultContent="/taipy-content/taipyStatic0/fred.png',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_image_bad_file_builder(gui: Gui, test_client, helpers):
    with open(os.path.abspath(__file__), "rb") as content:
        gui._bind_var_val("content", content.read())
        with tgb.Page(frame=None) as page:
            tgb.image(content="{content}")  # type: ignore[attr-defined]
        expected_list = [
            "<Image",
            'defaultContent="Invalid content: text/x',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_builder(gui, page, expected_list)
