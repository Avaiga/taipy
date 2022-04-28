# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
from taipy.gui import Gui


def test_chart_md_1(gui: Gui, helpers, csvdata):
    selected_indices = [14258]
    subplot_layout = {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    md_string = "<|{csvdata}|chart|x=Day|selected_color=green|y[1]=Daily hospital occupancy|label[1]=Entity|y[2]=Daily hospital occupancy|label[2]=Code|mode[2]=markers|color[2]=red|type[2]=scatter|xaxis[2]=x2|layout={subplot_layout}|on_range_change=range_change|width=100%|height=100%|selected={selected_indices}|>"
    expected_list = [
        "<Chart",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: &#x7B;&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;&#x7D;}"',
        'tp_onRangeChange="range_change"',
        'updateVars="selected0=selected_indices;selected1=selected_indices"',
        'updateVarName="_TpD_csvdata"',
        "data={_TpD_csvdata}",
        'width="100%"',
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_md(gui, md_string, expected_list)


def test_chart_html_1(gui: Gui, helpers, csvdata):
    selected_indices = [14258]
    subplot_layout = {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    html_string = '<taipy:chart data="{csvdata}" x="Day" selected_color="green" y[1]="Daily hospital occupancy" label[1]="Entity" y[2]="Daily hospital occupancy" label[2]="Code" mode[2]="markers" color[2]="red" type[2]="scatter" xaxis[2]="x2" layout="{subplot_layout}" on_range_change="range_change" width="100%" height="100%" selected="{selected_indices}"  />'
    expected_list = [
        "<Chart",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: &#x7B;&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;&#x7D;}"',
        'tp_onRangeChange="range_change"',
        'updateVars="selected0=selected_indices;selected1=selected_indices"',
        'updateVarName="_TpD_csvdata"',
        "data={_TpD_csvdata}",
        'width="100%"',
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_html(gui, html_string, expected_list)


def test_chart_html_2(gui: Gui, helpers, csvdata):
    selected_indices = [14258]
    subplot_layout = {"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}}
    html_string = '<taipy:chart x="Day" selected_color="green" y[1]="Daily hospital occupancy" label[1]="Entity" y[2]="Daily hospital occupancy" label[2]="Code" mode[2]="markers" color[2]="red" type[2]="scatter" xaxis[2]="x2" layout="{subplot_layout}" on_range_change="range_change" width="100%" height="100%" selected="{selected_indices}" >{csvdata}</taipy:chart>'
    expected_list = [
        "<Chart",
        "selected0={selected_indices}",
        "selected1={selected_indices}",
        'height="100%"',
        'layout="{&quot;grid&quot;: &#x7B;&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;&#x7D;}"',
        'tp_onRangeChange="range_change"',
        'updateVars="selected0=selected_indices;selected1=selected_indices"',
        'updateVarName="_TpD_csvdata"',
        "data={_TpD_csvdata}",
        'width="100%"',
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_html(gui, html_string, expected_list)

def test_map_md(gui: Gui, helpers):
    mapData = {
        "Lat": [
            48.4113, 18.0057, 48.6163, 48.5379, 48.5843, 48.612, 48.6286, 48.6068, 48.4489, 48.6548, 18.5721, 48.3734,
            17.6398, 48.5765, 48.4407, 48.2286,
        ],
        "Lon": [
            -112.8352, -65.804, -113.4784, -114.0702, -111.0188, -110.7939, -109.4629, -114.9123, -112.9705, -113.965,
            -66.5401, -111.5245, -64.7246, -112.1932, -113.3159, -104.5863,
        ],
        "Globvalue": [
            0.0875, 0.0892, 0.0908, 0.0933, 0.0942, 0.095, 0.095, 0.095, 0.0958, 0.0958, 0.0958, 0.0958, 0.0958, 0.0975,
            0.0983, 0.0992,
        ],
    }
    marker = { "color": "fuchsia", "size": 4 }
    layout = {
			"dragmode": "zoom",
			"mapbox": { "style": "open-street-map", "center": { "lat": 38, "lon": -90 }, "zoom": 3 },
			"margin": { "r": 0, "t": 0, "b": 0, "l": 0 }
		}
    md = "<|{mapData}|chart|type=scattermapbox|marker={marker}|layout={layout}|lat=Lat|lon=Lon|text=Globvalue|mode=markers|>"
    gui._set_frame(inspect.currentframe())
    expected_list = [
        "<Chart",
        '&quot;Lat&quot;: &#x7B;&quot;index&quot;:',
        '&quot;Lon&quot;: &#x7B;&quot;index&quot;:',
        'data={_TpD_mapData}',
        'layout="{&quot;dragmode&quot;: &quot;zoom&quot;, &quot;mapbox&quot;: &#x7B;&quot;style&quot;: &quot;open-street-map&quot;, &quot;center&quot;: &#x7B;&quot;lat&quot;: 38, &quot;lon&quot;: -90&#x7D;, &quot;zoom&quot;: 3&#x7D;, &quot;margin&quot;: &#x7B;&quot;r&quot;: 0, &quot;t&quot;: 0, &quot;b&quot;: 0, &quot;l&quot;: 0&#x7D;}"',
        'updateVarName="_TpD_mapData"',
    ]
    helpers.test_control_md(gui, md, expected_list)