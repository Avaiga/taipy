from taipy.gui import Gui


def test_status_md(gui: Gui, helpers):
    gui.bind_var_val("status", [{"status": "info", "message": "Info Message"}])
    md_string = "<|{status}|status|>"
    expected_list = [
        "<Status",
        'defaultValue="[{&quot;status&quot;: &quot;info&quot;, &quot;message&quot;: &quot;Info Message&quot;}]"',
        "value={status}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_status_html(gui: Gui, helpers):
    gui.bind_var_val("status", [{"status": "info", "message": "Info Message"}])
    html_string = '<taipy:status value="{status}" />'
    expected_list = [
        "<Status",
        'defaultValue="[{&quot;status&quot;: &quot;info&quot;, &quot;message&quot;: &quot;Info Message&quot;}]"',
        "value={status}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
