from taipy.gui import Gui
from datetime import datetime
import pandas as pd

def text_chart_md_1(gui: Gui, helpers):
    gui.bind_var_val("date", datetime.strptime('15 Dec 2020', '%d %b %Y'))
    md_string = "<|{date}|date_selector|>"
    expected_list = ["<DateSelector", 'defaultValue="2020-12-','tp_varname="date"', "value={date}"]
    helpers.test_control_md(gui, md_string, expected_list)

def text_chart_md_2(gui: Gui, helpers):
    gui.bind_var_val("date", datetime.strptime('15 Dec 2020', '%d %b %Y'))
    md_string = "<|{date}|date_selector|with_time|>"
    expected_list = ["<DateSelector", 'defaultValue="2020-12-','tp_varname="date"', "value={date}", "withTime={true}"]
    helpers.test_control_md(gui, md_string, expected_list)

def text_chart_html_1(gui: Gui, helpers):
    gui.bind_var_val("date", datetime.strptime('15 Dec 2020', '%d %b %Y'))
    html_string = '<taipy:date_selector date="{date}" />'
    expected_list = ["<DateSelector", 'defaultValue="2020-12-','tp_varname="date"', "value={date}"]
    helpers.test_control_html(gui, html_string, expected_list)

def text_chart_html_2(gui: Gui, helpers):
    gui.bind_var_val("date", datetime.strptime('15 Dec 2020', '%d %b %Y'))
    html_string = '<taipy:date_selector>{date}</taipy:date_selector>'
    expected_list = ["<DateSelector", 'defaultValue="2020-12-','tp_varname="date"', "value={date}"]
    helpers.test_control_html(gui, html_string, expected_list)
