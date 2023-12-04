# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime
import inspect
import random
import typing as t

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_chart_builder_1(gui: Gui, helpers, csvdata):
    selected_indices = [14258]  # noqa: F841
    subplot_layout = {  # noqa: F841
        "grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}
    }
    y = ["Daily hospital occupancy", "Daily hospital occupancy"]  # noqa: F841
    label = ["Entity", "Code"]  # noqa: F841
    mode = [None, "markers"]  # noqa: F841
    color = [None, "red"]  # noqa: F841
    chart_type = [None, "scatter"]  # noqa: F841
    xaxis = [None, "x2"]  # noqa: F841
    with tgb.Page(frame=None) as page:
        tgb.chart(
            data="{csvdata}",
            x="Day",
            selected_color="green",
            y="{y}",
            label="{label}",
            mode="{mode}",
            color="{color}",
            type="{chart_type}",
            xaxis="{xaxis}",
            layout="{subplot_layout}",
            on_range_change="range_change",
            width="100%",
            height="100%",
            selected="{selected_indices}",
        )
    expected_list = [
        "<Chart",
        "selected0={tpec_TpExPr_selected_indices_TPMDL_0}",
        "selected1={tpec_TpExPr_selected_indices_TPMDL_0}",
        'height="100%"',
        'defaultLayout="{&quot;grid&quot;: &#x7B;&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;&#x7D;}"',
        'onRangeChange="range_change"',
        'updateVars="layout=_TpDi_tpec_TpExPr_subplot_layout_TPMDL_0;selected0=tpec_TpExPr_selected_indices_TPMDL_0;selected1=tpec_TpExPr_selected_indices_TPMDL_0"',
        'updateVarName="_TpD_tpec_TpExPr_csvdata_TPMDL_0"',
        "data={_TpD_tpec_TpExPr_csvdata_TPMDL_0}",
        'width="100%"',
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_builder(gui, page, expected_list)


def test_chart_builder_2(gui: Gui, helpers, csvdata):
    selected_indices = [14258]  # noqa: F841
    with tgb.Page(frame=None) as page:
        tgb.chart(
            data="{csvdata}",
            x="Day",
            selected_color="green",
            y=["Daily hospital occupancy", "Daily hospital occupancy"],
            label=["Entity", "Code"],
            mode=[None, "markers"],
            color=[None, "red"],
            type=(None, "scatter"),
            xaxis=(None, "x2"),
            layout={"grid": {"rows": 1, "columns": 2, "subplots": [["xy", "x2y"]], "roworder": "bottom to top"}},
            on_range_change="range_change",
            width="100%",
            height="100%",
            selected="{selected_indices}",
        )
    expected_list = [
        "<Chart",
        "selected0={tpec_TpExPr_selected_indices_TPMDL_0}",
        "selected1={tpec_TpExPr_selected_indices_TPMDL_0}",
        'height="100%"',
        'defaultLayout="{&quot;grid&quot;: &#x7B;&quot;rows&quot;: 1, &quot;columns&quot;: 2, &quot;subplots&quot;: [[&quot;xy&quot;, &quot;x2y&quot;]], &quot;roworder&quot;: &quot;bottom to top&quot;&#x7D;}"',
        'onRangeChange="range_change"',
        'updateVars="selected0=tpec_TpExPr_selected_indices_TPMDL_0;selected1=tpec_TpExPr_selected_indices_TPMDL_0"',
        'updateVarName="_TpD_tpec_TpExPr_csvdata_TPMDL_0"',
        "data={_TpD_tpec_TpExPr_csvdata_TPMDL_0}",
        'width="100%"',
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_builder(gui, page, expected_list)


def test_map_builder(gui: Gui, helpers):
    mapData = {  # noqa: F841
        "Lat": [
            48.4113,
            18.0057,
            48.6163,
            48.5379,
            48.5843,
            48.612,
            48.6286,
            48.6068,
            48.4489,
            48.6548,
            18.5721,
            48.3734,
            17.6398,
            48.5765,
            48.4407,
            48.2286,
        ],
        "Lon": [
            -112.8352,
            -65.804,
            -113.4784,
            -114.0702,
            -111.0188,
            -110.7939,
            -109.4629,
            -114.9123,
            -112.9705,
            -113.965,
            -66.5401,
            -111.5245,
            -64.7246,
            -112.1932,
            -113.3159,
            -104.5863,
        ],
        "Globvalue": [
            0.0875,
            0.0892,
            0.0908,
            0.0933,
            0.0942,
            0.095,
            0.095,
            0.095,
            0.0958,
            0.0958,
            0.0958,
            0.0958,
            0.0958,
            0.0975,
            0.0983,
            0.0992,
        ],
    }
    marker = {"color": "fuchsia", "size": 4}  # noqa: F841
    layout = {  # noqa: F841
        "dragmode": "zoom",
        "mapbox": {"style": "open-street-map", "center": {"lat": 38, "lon": -90}, "zoom": 3},
        "margin": {"r": 0, "t": 0, "b": 0, "l": 0},
    }
    with tgb.Page(frame=None) as page:
        tgb.chart(
            data="{mapData}",
            type="scattermapbox",
            marker="{marker}",
            layout="{layout}",
            lat="Lat",
            lon="Lon",
            text="Globvalue",
            mode="markers",
        )
    gui._set_frame(inspect.currentframe())
    expected_list = [
        "<Chart",
        "&quot;Lat&quot;: &#x7B;&quot;index&quot;:",
        "&quot;Lon&quot;: &#x7B;&quot;index&quot;:",
        "data={_TpD_tpec_TpExPr_mapData_TPMDL_0}",
        'defaultLayout="{&quot;dragmode&quot;: &quot;zoom&quot;, &quot;mapbox&quot;: &#x7B;&quot;style&quot;: &quot;open-street-map&quot;, &quot;center&quot;: &#x7B;&quot;lat&quot;: 38, &quot;lon&quot;: -90&#x7D;, &quot;zoom&quot;: 3&#x7D;, &quot;margin&quot;: &#x7B;&quot;r&quot;: 0, &quot;t&quot;: 0, &quot;b&quot;: 0, &quot;l&quot;: 0&#x7D;}"',
        'updateVarName="_TpD_tpec_TpExPr_mapData_TPMDL_0"',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_chart_indexed_properties_builder(gui: Gui, helpers):
    data: t.Dict[str, t.Any] = {}
    data["Date"] = [datetime.datetime(2021, 12, i) for i in range(1, 31)]

    data["La Rochelle"] = [10 + 6 * random.random() for _ in range(1, 31)]
    data["Montpellier"] = [16 + 6 * random.random() for _ in range(1, 31)]
    data["Paris"] = [6 + 6 * random.random() for _ in range(1, 31)]

    data["La Rochelle 1"] = [x * (1 + (random.random() / 10)) for x in data["La Rochelle"]]
    data["La Rochelle 2"] = [x * (1 - (random.random() / 10)) for x in data["La Rochelle"]]

    data["Montpellier 1"] = [x * (1 + (random.random() / 10)) for x in data["Montpellier"]]
    data["Montpellier 2"] = [x * (1 - (random.random() / 10)) for x in data["Montpellier"]]

    with tgb.Page(frame=None) as page:
        tgb.chart(
            data="{data}",
            x="Date",
            mode="lines",
            y=["La Rochelle", "La Rochelle 1", "La Rochelle 2", "Montpellier", "Montpellier 1", "Montpellier 2"],
            line=[None, "dashdot", "dash", None, "dashdot", "dash"],
            color=[None, "blue", "blue", None, "red", "red"],
        )

    gui._set_frame(inspect.currentframe())
    expected_list = [
        "<Chart",
        "&quot;traces&quot;: [[&quot;Date_str&quot;, &quot;La Rochelle&quot;], [&quot;Date_str&quot;, &quot;La Rochelle 1&quot;], [&quot;Date_str&quot;, &quot;La Rochelle 2&quot;], [&quot;Date_str&quot;, &quot;Montpellier&quot;], [&quot;Date_str&quot;, &quot;Montpellier 1&quot;], [&quot;Date_str&quot;, &quot;Montpellier 2&quot;]]",
        "&quot;lines&quot;: [null, &#x7B;&quot;dash&quot;: &quot;dashdot&quot;&#x7D;, &#x7B;&quot;dash&quot;: &quot;dash&quot;&#x7D;, null, &#x7B;&quot;dash&quot;: &quot;dashdot&quot;&#x7D;, &#x7B;&quot;dash&quot;: &quot;dash&quot;&#x7D;]",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_chart_indexed_properties_with_arrays_builder(gui: Gui, helpers):
    data: t.Dict[str, t.Any] = {}
    data["Date"] = [datetime.datetime(2021, 12, i) for i in range(1, 31)]

    data["La Rochelle"] = [10 + 6 * random.random() for _ in range(1, 31)]
    data["Montpellier"] = [16 + 6 * random.random() for _ in range(1, 31)]
    data["Paris"] = [6 + 6 * random.random() for _ in range(1, 31)]

    data["La Rochelle 1"] = [x * (1 + (random.random() / 10)) for x in data["La Rochelle"]]
    data["La Rochelle 2"] = [x * (1 - (random.random() / 10)) for x in data["La Rochelle"]]

    data["Montpellier 1"] = [x * (1 + (random.random() / 10)) for x in data["Montpellier"]]
    data["Montpellier 2"] = [x * (1 - (random.random() / 10)) for x in data["Montpellier"]]

    ys = [  # noqa: F841
        "La Rochelle",
        "La Rochelle 1",
        "La Rochelle 2",
        "Montpellier",
        "Montpellier 1",
        "Montpellier 2",
    ]
    lines = [None, "dashdot", "dash", None, "dashdot", "dash"]  # noqa: F841
    colors = [None, "blue", "blue", None, "red", "red"]  # noqa: F841

    with tgb.Page(frame=None) as page:
        tgb.chart(
            data="{data}",
            x="Date",
            mode="lines",
            y="{ys}",
            line="{lines}",
            color="{colors}",
        )

    gui._set_frame(inspect.currentframe())
    expected_list = [
        "<Chart",
        "&quot;traces&quot;: [[&quot;Date_str&quot;, &quot;La Rochelle&quot;], [&quot;Date_str&quot;, &quot;La Rochelle 1&quot;], [&quot;Date_str&quot;, &quot;La Rochelle 2&quot;], [&quot;Date_str&quot;, &quot;Montpellier&quot;], [&quot;Date_str&quot;, &quot;Montpellier 1&quot;], [&quot;Date_str&quot;, &quot;Montpellier 2&quot;]]",
        "&quot;lines&quot;: [null, &#x7B;&quot;dash&quot;: &quot;dashdot&quot;&#x7D;, &#x7B;&quot;dash&quot;: &quot;dash&quot;&#x7D;, null, &#x7B;&quot;dash&quot;: &quot;dashdot&quot;&#x7D;, &#x7B;&quot;dash&quot;: &quot;dash&quot;&#x7D;]",
    ]
    helpers.test_control_builder(gui, page, expected_list)
