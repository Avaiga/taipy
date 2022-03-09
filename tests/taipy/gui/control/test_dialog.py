from taipy.gui import Gui, Markdown


def test_dialog_md_1(gui: Gui, helpers):
    gui._bind_var_val("dialog_open", False)
    md_string = "<|dialog|title=This is a Dialog|open={dialog_open}|page=page_test|on_validate=validate_action|on_cancel=cancel_action|>"
    expected_list = [
        "<Dialog",
        'tp_onCancel="cancel_action"',
        'cancelLabel="Cancel"',
        'page="page_test"',
        'title="This is a Dialog"',
        'tp_onValidate="validate_action"',
        'validateLabel="Validate"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_md_2(gui: Gui, helpers):
    partial = gui.add_partial(Markdown("# A partial"))
    gui._bind_var_val("dialog_open", False)
    gui._bind_var_val("partial", partial)
    md_string = "<|dialog|title=Another Dialog|open={dialog_open}|partial={partial}|on_validate=validate_action|>"
    expected_list = [
        "<Dialog",
        'cancelLabel="Cancel"',
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_onValidate="validate_action"',
        'validateLabel="Validate"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_html_1(gui: Gui, helpers, csvdata):
    gui._bind_var_val("dialog_open", False)
    html_string = '<taipy:dialog title="This is a Dialog" open="{dialog_open}" page="page1" on_validate="validate_action" on_cancel="cancel_action" />'
    expected_list = [
        "<Dialog",
        'tp_onCancel="cancel_action"',
        'cancelLabel="Cancel"',
        'page="page1"',
        'title="This is a Dialog"',
        'tp_onValidate="validate_action"',
        'validateLabel="Validate"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_dialog_html_2(gui: Gui, helpers, csvdata):
    partial = gui.add_partial(Markdown("# A partial"))
    gui._bind_var_val("dialog_open", False)
    gui._bind_var_val("partial", partial)
    html_string = (
        '<taipy:dialog title="Another Dialog" open="{dialog_open}" partial="{partial}" on_validate="validate_action" />'
    )
    expected_list = [
        "<Dialog",
        'cancelLabel="Cancel"',
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_onValidate="validate_action"',
        'validateLabel="Validate"',
        'updateVarName="_TpB_dialog_open"',
        "open={_TpB_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
