from taipy.gui import Gui


def test_chart_md_1(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    gui.bind_var_val("selected_indices", [14258])
    gui.bind_var_val(
        "subplot_layout", {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    )
    md_string = "<|{csvdata}|chart|x=Day|selected_color=green|y[1]=Daily hospital occupancy|label[1]=Entity|y[2]=Daily hospital occupancy|label[2]=Code|mode[2]=markers|color[2]=red|type[2]=scatter|xaxis[2]=x2|layout={subplot_layout}|range_change=range_change|width=100%|height=100%|selected={selected_indices}|>"
    expected_list = [
        "<Chart",
        "refresh={csvdata__refresh}",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: {&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;}}"',
        'rangeChange="range_change"',
        'tp_updatevars="selected0=selected_indices;selected1=selected_indices"',
        'tp_varname="csvdata"',
        "data={csvdata}",
        'width="100%"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_chart_html_1(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    gui.bind_var_val("selected_indices", [14258])
    gui.bind_var_val(
        "subplot_layout", {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    )
    html_string = '<taipy:chart data="{csvdata}" x="Day" selected_color="green" y[1]="Daily hospital occupancy" label[1]="Entity" y[2]="Daily hospital occupancy" label[2]="Code" mode[2]="markers" color[2]="red" type[2]="scatter" xaxis[2]="x2" layout="{subplot_layout}" range_change="range_change" width="100%" height="100%" selected="{selected_indices}"  />'
    expected_list = [
        "<Chart",
        "refresh={csvdata__refresh}",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: {&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;}}"',
        'rangeChange="range_change"',
        'tp_updatevars="selected0=selected_indices;selected1=selected_indices"',
        'tp_varname="csvdata"',
        "data={csvdata}",
        'width="100%"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_chart_html_2(gui: Gui, helpers, csvdata):
    gui.bind_var_val("csvdata", csvdata)
    gui.bind_var_val("selected_indices", [14258])
    gui.bind_var_val(
        "subplot_layout", {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    )
    html_string = '<taipy:chart x="Day" selected_color="green" y[1]="Daily hospital occupancy" label[1]="Entity" y[2]="Daily hospital occupancy" label[2]="Code" mode[2]="markers" color[2]="red" type[2]="scatter" xaxis[2]="x2" layout="{subplot_layout}" range_change="range_change" width="100%" height="100%" selected="{selected_indices}" >{csvdata}</taipy:chart>'
    expected_list = [
        "<Chart",
        "refresh={csvdata__refresh}",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: {&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;}}"',
        'rangeChange="range_change"',
        'tp_updatevars="selected0=selected_indices;selected1=selected_indices"',
        'tp_varname="csvdata"',
        "data={csvdata}",
        'width="100%"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
