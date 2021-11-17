from taipy.gui import Gui


def test_navbar_md(gui: Gui, helpers):
    gui.bind_var_val(
        "navlov",
        [
            ("/page1", "Page 1"),
            ("/page2", "Page 2"),
            ("/page3", "Page 3"),
            ("/page4", "Page 4"),
        ],
    )
    md_string = "<|navbar|lov={navlov}|>"
    expected_list = [
        "<NavBar",
        'defaultValue="-1"',
        'defaultLov="[[&quot;/page1&quot;, &quot;Page 1&quot;], [&quot;/page2&quot;, &quot;Page 2&quot;], [&quot;/page3&quot;, &quot;Page 3&quot;], [&quot;/page4&quot;, &quot;Page 4&quot;]]"',
        "lov={navlov}",
        ' value=""',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_navbar_html(gui: Gui, helpers):
    gui.bind_var_val(
        "navlov",
        [
            ("/page1", "Page 1"),
            ("/page2", "Page 2"),
            ("/page3", "Page 3"),
            ("/page4", "Page 4"),
        ],
    )
    html_string = '<taipy:navbar lov="{navlov}" />'
    expected_list = [
        "<NavBar",
        'defaultValue="-1"',
        'defaultLov="[[&quot;/page1&quot;, &quot;Page 1&quot;], [&quot;/page2&quot;, &quot;Page 2&quot;], [&quot;/page3&quot;, &quot;Page 3&quot;], [&quot;/page4&quot;, &quot;Page 4&quot;]]"',
        "lov={navlov}",
        ' value=""',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
