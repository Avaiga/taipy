from datetime import datetime

from taipy.gui import Gui


def test_date_md_1(gui: Gui, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    md_string = "<|{date}|date|>"
    expected_list = ["<DateSelector", 'defaultDate="2020-12-', 'updateVarName="_TpDt_date"', "date={_TpDt_date}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_date_md_2(gui: Gui, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    md_string = "<|{date}|date|with_time|>"
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_date"',
        "date={_TpDt_date}",
        "withTime={true}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_date_html_1(gui: Gui, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    html_string = '<taipy:date date="{date}" />'
    expected_list = ["<DateSelector", 'defaultDate="2020-12-', 'updateVarName="_TpDt_date"', "date={_TpDt_date}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_date_html_2(gui: Gui, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    html_string = "<taipy:date>{date}</taipy:date>"
    expected_list = ["<DateSelector", 'defaultDate="2020-12-', 'updateVarName="_TpDt_date"', "date={_TpDt_date}"]
    helpers.test_control_html(gui, html_string, expected_list)
