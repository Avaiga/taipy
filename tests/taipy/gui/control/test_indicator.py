from taipy.gui import Gui


def test_indicator_md(gui: Gui, helpers):
    gui.bind_var_val("val", 15)
    md_string = "<|12|indicator|value={val}|min=1|max=20|format=%.2f|>"
    expected_list = [
        "<Indicator",
        'className="taipy-indicator"',
        "defaultValue={15}",
        "display={12.0}",
        'format="%.2f"',
        "max={20.0}",
        "min={1.0}",
        "value={val}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_menu_html(gui: Gui, helpers):
    gui.bind_var_val("val", 15)
    html_string = '<taipy:indicator value="{val}" min="1" max="20" format="%.2f" >12</taipy:indicator>'
    expected_list = [
        "<Indicator",
        'className="taipy-indicator"',
        "defaultValue={15}",
        "display={12.0}",
        'format="%.2f"',
        "max={20.0}",
        "min={1.0}",
        "value={val}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
