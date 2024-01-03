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

from taipy.gui import Gui


def test_expandable_md_1(gui: Gui, helpers):
    md_string = """
<|Expandable section|expandable|not expanded|
# This is an expandable section
|>
"""
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expandable_md_2(gui: Gui, helpers):
    md_string = """
<|expandable.start|title=Expandable section|not expanded|>
# This is an expandable section
<|expandable.end|>
"""
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expandable_html(gui: Gui, helpers):
    html_string = '<taipy:expandable title="Expandable section" expanded="false"><h1>This is an expandable section</h1></taipy:expandable >'
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
