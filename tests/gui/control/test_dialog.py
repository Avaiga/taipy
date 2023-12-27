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

from taipy.gui import Gui, Markdown


def test_dialog_md_1(gui: Gui, helpers):
    dialog_open = False  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|dialog|title=This is a Dialog|open={dialog_open}|page=page_test|on_action=validate_action|>"
    expected_list = [
        "<Dialog",
        'onAction="validate_action"',
        'page="page_test"',
        'title="This is a Dialog"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_md_2(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    partial = gui.add_partial(Markdown("# A partial"))  # noqa: F841
    dialog_open = False  # noqa: F841
    md_string = "<|dialog|title=Another Dialog|open={dialog_open}|partial={partial}|on_action=validate_action|>"
    expected_list = [
        "<Dialog",
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'onAction="validate_action"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_labels_md(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    dialog_open = False  # noqa: F841
    md_string = (
        "<|dialog|title=Another Dialog|open={dialog_open}|page=page_test|labels=Cancel;Validate|close_label=MYClose|>"
    )
    expected_list = [
        "<Dialog",
        'page="page_test"',
        'title="Another Dialog"',
        'labels="[&quot;Cancel&quot;, &quot;Validate&quot;]"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        'closeLabel="MYClose"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_html_1(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    dialog_open = False  # noqa: F841
    html_string = (
        '<taipy:dialog title="This is a Dialog" open="{dialog_open}" page="page1" on_action="validate_action" />'
    )
    expected_list = [
        "<Dialog",
        'page="page1"',
        'title="This is a Dialog"',
        'onAction="validate_action"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_dialog_html_2(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    partial = gui.add_partial(Markdown("# A partial"))  # noqa: F841
    dialog_open = False  # noqa: F841
    html_string = (
        '<taipy:dialog title="Another Dialog" open="{dialog_open}" partial="{partial}" on_action="validate_action" />'
    )
    expected_list = [
        "<Dialog",
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'onAction="validate_action"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_dialog_labels_html(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    dialog_open = False  # noqa: F841
    html_string = (
        '<taipy:dialog title="Another Dialog" open="{dialog_open}" page="page_test" labels="Cancel;Validate" />'
    )
    expected_list = [
        "<Dialog",
        'page="page_test"',
        'title="Another Dialog"',
        'labels="[&quot;Cancel&quot;, &quot;Validate&quot;]"',
        'updateVarName="_TpB_tpec_TpExPr_dialog_open_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_dialog_open_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
