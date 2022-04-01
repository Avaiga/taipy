import inspect
from taipy.gui import Gui, Markdown


def test_dialog_md_1(gui: Gui, helpers):
    dialog_open = False
    gui._set_frame(inspect.currentframe())
    md_string = "<|dialog|title=This is a Dialog|open={dialog_open}|page=page_test|on_action=validate_action|>"
    expected_list = [
        "<Dialog",
        'tp_onAction="validate_action"',
        'page="page_test"',
        'title="This is a Dialog"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_md_2(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    partial = gui.add_partial(Markdown("# A partial"))
    dialog_open = False
    md_string = "<|dialog|title=Another Dialog|open={dialog_open}|partial={partial}|on_action=validate_action|>"
    expected_list = [
        "<Dialog",
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_onAction="validate_action"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)

def test_dialog_labels_md(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    dialog_open = False
    md_string = "<|dialog|title=Another Dialog|open={dialog_open}|page=page_test|labels=Cancel;Validate|close_label=MYClose|>"
    expected_list = [
        "<Dialog",
        'page="page_test"',
        'title="Another Dialog"',
        'labels="[&quot;Cancel&quot;, &quot;Validate&quot;]"',
        'updateVarName="_TpB_dialog_open"',
        'closeLabel="MYClose"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_html_1(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    dialog_open = False
    html_string = '<taipy:dialog title="This is a Dialog" open="{dialog_open}" page="page1" on_action="validate_action" />'
    expected_list = [
        "<Dialog",
        'page="page1"',
        'title="This is a Dialog"',
        'tp_onAction="validate_action"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_dialog_html_2(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    partial = gui.add_partial(Markdown("# A partial"))
    dialog_open = False
    html_string = (
        '<taipy:dialog title="Another Dialog" open="{dialog_open}" partial="{partial}" on_action="validate_action" />'
    )
    expected_list = [
        "<Dialog",
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_onAction="validate_action"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)

def test_dialog_labels_html(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    dialog_open = False
    html_string = '<taipy:dialog title="Another Dialog" open="{dialog_open}" page="page_test" labels="Cancel;Validate" />'
    expected_list = [
        "<Dialog",
        'page="page_test"',
        'title="Another Dialog"',
        'labels="[&quot;Cancel&quot;, &quot;Validate&quot;]"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)