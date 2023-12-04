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

import pytest

from taipy.gui import Gui


def test_invalid_control_name(gui: Gui, helpers):
    md_string = "<|invalid|invalid|>"
    expected_list = ["INVALID SYNTAX - Control is 'invalid'"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_value_to_negated_property(gui: Gui, helpers):
    md_string = "<|button|not active=true|>"
    expected_list = ["<Button", "active={false}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_invalid_property_value(gui: Gui, helpers):
    md_string = "<|button|let's try that!|>"
    expected_list = ["<Button", 'label="&lt;Empty&gt;"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_unclosed_block(gui: Gui, helpers):
    md_string = "<|"
    expected_list = ["<Part", "</Part>"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_opening_unknown_block(gui: Gui, helpers):
    md_string = "<|unknown"
    expected_list = ["<Part", 'className="unknown"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_closing_unknown_block(gui: Gui, helpers):
    md_string = "|>"
    expected_list = ["<div>", "No matching opened tag", "</div>"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_md_link(gui: Gui, helpers):
    md_string = "[content](link)"
    expected_list = ["<a", 'href="link"', "content</a>"]
    helpers.test_control_md(gui, md_string, expected_list)
