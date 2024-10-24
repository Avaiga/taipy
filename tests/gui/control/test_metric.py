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

def test_metric_md_none(gui: Gui, helpers):
    md_string = "<|metric|type=None|value=42|>"
    expected_list = ["<Metric", 'type="None"', 'value="42"']
    helpers.test_control_md(gui, md_string, expected_list)

def test_metric_md_none_lowercase(gui: Gui, helpers):
    md_string = "<|metric|type=none|value=42|>"
    expected_list = ["<Metric", 'type="none"', 'value="42"']
    helpers.test_control_md(gui, md_string, expected_list)

def test_metric_md_circular(gui: Gui, helpers):
    md_string = "<|metric|type=circular|value=42|>"
    expected_list = ["<Metric", 'type="circular"', 'value="42"']
    helpers.test_control_md(gui, md_string, expected_list)

def test_metric_md_linear(gui: Gui, helpers):
    md_string = "<|metric|type=linear|value=42|>"
    expected_list = ["<Metric", 'type="linear"', 'value="42"']
    helpers.test_control_md(gui, md_string, expected_list)

def test_metric_html_none(gui: Gui, helpers):
    html_string = '<taipy:metric type="None" value="42" />'
    expected_list = ["<Metric", 'type="None"', 'value="42"']
    helpers.test_control_html(gui, html_string, expected_list)

def test_metric_html_none_lowercase(gui: Gui, helpers):
    html_string = '<taipy:metric type="none" value="42" />'
    expected_list = ["<Metric", 'type="none"', 'value="42"']
    helpers.test_control_html(gui, html_string, expected_list)

def test_metric_html_circular(gui: Gui, helpers):
    html_string = '<taipy:metric type="circular" value="42" />'
    expected_list = ["<Metric", 'type="circular"', 'value="42"']
    helpers.test_control_html(gui, html_string, expected_list)

def test_metric_html_linear(gui: Gui, helpers):
    html_string = '<taipy:metric type="linear" value="42" />'
    expected_list = ["<Metric", 'type="linear"', 'value="42"']
    helpers.test_control_html(gui, html_string, expected_list)
