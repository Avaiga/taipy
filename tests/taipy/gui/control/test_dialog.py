from taipy.gui import Gui, Markdown


def test_dialog_md_1(gui: Gui, helpers):
    gui.bind_var_val("dialog_open", False)
    md_string = "<|dialog|title=This is a Dialog|open={dialog_open}|page=page_test|validate_action=validate_action|cancel_action=cancel_action|>"
    expected_list = [
        "<Dialog",
        'cancelAction="cancel_action"',
        'cancelLabel="Cancel"',
        'page="page_test"',
        'title="This is a Dialog"',
        'tp_varname="TaipyBool_dialog_open"',
        'validateAction="validate_action"',
        'validateLabel="Validate"',
        "open={TaipyBool_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_md_2(gui: Gui, helpers):
    partial = gui.add_partial(Markdown("# A partial"))
    gui.bind_var_val("dialog_open", False)
    gui.bind_var_val("partial", partial)
    md_string = "<|dialog|title=Another Dialog|open={dialog_open}|partial={partial}|validate_action=validate_action|>"
    expected_list = [
        "<Dialog",
        'cancelLabel="Cancel"',
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_varname="TaipyBool_dialog_open"',
        'validateAction="validate_action"',
        'validateLabel="Validate"',
        "open={TaipyBool_dialog_open}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_dialog_html_1(gui: Gui, helpers, csvdata):
    gui.bind_var_val("dialog_open", False)
    html_string = '<taipy:dialog title="This is a Dialog" open="{dialog_open}" page="page1" validate_action="validate_action" cancel_action="cancel_action" />'
    expected_list = [
        "<Dialog",
        'cancelAction="cancel_action"',
        'cancelLabel="Cancel"',
        'page="page1"',
        'title="This is a Dialog"',
        'tp_varname="TaipyBool_dialog_open"',
        'validateAction="validate_action"',
        'validateLabel="Validate"',
        "open={TaipyBool_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_dialog_html_2(gui: Gui, helpers, csvdata):
    partial = gui.add_partial(Markdown("# A partial"))
    gui.bind_var_val("dialog_open", False)
    gui.bind_var_val("partial", partial)
    html_string = '<taipy:dialog title="Another Dialog" open="{dialog_open}" partial="{partial}" validate_action="validate_action" />'
    expected_list = [
        "<Dialog",
        'cancelLabel="Cancel"',
        'page="TaiPy_partials',
        'title="Another Dialog"',
        'tp_varname="TaipyBool_dialog_open"',
        'validateAction="validate_action"',
        'validateLabel="Validate"',
        "open={TaipyBool_dialog_open}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
