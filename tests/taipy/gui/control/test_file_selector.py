from taipy.gui import Gui


def test_file_selector_md(gui: Gui, helpers):
    gui._bind_var_val("content", None)
    md_string = "<|{content}|file_selector|label=label|on_action=action|>"
    expected_list = [
        "<FileSelector",
        'updateVarName="content"',
        'label="label"',
        'tp_onAction="action"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_file_selector_html(gui: Gui, helpers):
    gui._bind_var_val("content", None)
    html_string = '<taipy:file_selector content="{content}" label="label" on_action="action" />'
    expected_list = [
        "<FileSelector",
        'updateVarName="content"',
        'label="label"',
        'tp_onAction="action"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
