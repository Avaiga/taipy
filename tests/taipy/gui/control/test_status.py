import inspect
from taipy.gui import Gui


def test_status_md(gui: Gui, helpers):
    status = [{"status": "info", "message": "Info Message"}]
    md_string = "<|{status}|status|>"
    expected_list = [
        "<Status",
        'defaultValue="[&#x7B;&quot;status&quot;: &quot;info&quot;, &quot;message&quot;: &quot;Info Message&quot;&#x7D;]"',
        "value={status}",
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_md(gui, md_string, expected_list)


def test_status_html(gui: Gui, helpers):
    status = [{"status": "info", "message": "Info Message"}]
    html_string = '<taipy:status value="{status}" />'
    expected_list = [
        "<Status",
        'defaultValue="[&#x7B;&quot;status&quot;: &quot;info&quot;, &quot;message&quot;: &quot;Info Message&quot;&#x7D;]"',
        "value={status}",
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_html(gui, html_string, expected_list)
