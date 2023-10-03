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


import re
import typing as t
from enum import Enum

from .._renderers.utils import _get_columns_dict
from .._warnings import _warn
from ..types import PropertyType
from ..utils import _MapDict

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Chart_iprops(Enum):
    x = 0
    y = 1
    z = 2
    label = 3
    text = 4
    mode = 5
    type = 6
    color = 7
    xaxis = 8
    yaxis = 9
    selected_color = 10
    marker = 11
    selected_marker = 12
    orientation = 13
    _name = 14
    line = 15
    text_anchor = 16
    options = 17
    lon = 18
    lat = 19
    base = 20
    r = 21
    theta = 22
    close = 23
    open = 24
    high = 25
    low = 26
    locations = 27
    values = 28
    labels = 29
    decimator = 30
    measure = 31
    parents = 32


__CHART_AXIS: t.Dict[str, t.Tuple[_Chart_iprops, ...]] = {
    "bar": (_Chart_iprops.x, _Chart_iprops.y, _Chart_iprops.base),
    "candlestick": (
        _Chart_iprops.x,
        _Chart_iprops.close,
        _Chart_iprops.open,
        _Chart_iprops.high,
        _Chart_iprops.low,
    ),
    "choropleth": (_Chart_iprops.locations, _Chart_iprops.z),
    "densitymapbox": (_Chart_iprops.lon, _Chart_iprops.lat, _Chart_iprops.z),
    "funnelarea": (_Chart_iprops.values,),
    "pie": (_Chart_iprops.values, _Chart_iprops.labels),
    "scattergeo": (_Chart_iprops.lon, _Chart_iprops.lat),
    "scattermapbox": (_Chart_iprops.lon, _Chart_iprops.lat),
    "scatterpolar": (_Chart_iprops.r, _Chart_iprops.theta),
    "scatterpolargl": (_Chart_iprops.r, _Chart_iprops.theta),
    "treemap": (_Chart_iprops.labels, _Chart_iprops.parents, _Chart_iprops.values),
    "waterfall": (_Chart_iprops.x, _Chart_iprops.y, _Chart_iprops.measure),
}
__CHART_DEFAULT_AXIS: t.Tuple[_Chart_iprops, ...] = (_Chart_iprops.x, _Chart_iprops.y, _Chart_iprops.z)
__CHART_MARKER_TO_COLS: t.Tuple[str, ...] = ("color", "size", "symbol", "opacity")
__CHART_NO_INDEX: t.Tuple[str, ...] = ("pie", "histogram", "heatmap", "funnelarea")
_CHART_NAMES: t.Tuple[str, ...] = tuple(e.name[1:] if e.name[0] == "_" else e.name for e in _Chart_iprops)


def __check_dict(values: t.List[t.Any], properties: t.Iterable[_Chart_iprops]) -> None:
    for prop in properties:
        if values[prop.value] is not None and not isinstance(values[prop.value], (dict, _MapDict)):
            _warn(f"Property {prop.name} of chart control should be a dict.")
            values[prop.value] = None


def __get_multiple_indexed_attributes(
    attributes: t.Dict[str, t.Any], names: t.Iterable[str], index: t.Optional[int] = None
) -> t.List[t.Optional[str]]:
    names = names if index is None else [f"{n}[{index}]" for n in names]  # type: ignore
    return [attributes.get(name) for name in names]


__RE_INDEXED_DATA = re.compile(r"^(\d+)\/(.*)")


def __get_col_from_indexed(col_name: str, idx: int) -> t.Optional[str]:
    if re_res := __RE_INDEXED_DATA.search(col_name):
        return col_name if str(idx) == re_res.group(1) else None
    return col_name


def _build_chart_config(gui: "Gui", attributes: t.Dict[str, t.Any], col_types: t.Dict[str, str]):  # noqa: C901
    default_type = attributes.get("_default_type", "scatter")
    default_mode = attributes.get("_default_mode", "lines+markers")
    trace = __get_multiple_indexed_attributes(attributes, _CHART_NAMES)
    if not trace[_Chart_iprops.mode.value]:
        trace[_Chart_iprops.mode.value] = default_mode
    # type
    if not trace[_Chart_iprops.type.value]:
        trace[_Chart_iprops.type.value] = default_type
    if not trace[_Chart_iprops.xaxis.value]:
        trace[_Chart_iprops.xaxis.value] = "x"
    if not trace[_Chart_iprops.yaxis.value]:
        trace[_Chart_iprops.yaxis.value] = "y"
    # Indexed properties: Check for arrays
    for prop in _Chart_iprops:
        values = trace[prop.value]
        if isinstance(values, (list, tuple)) and len(values):
            prop_name = prop.name[1:] if prop.name[0] == "_" else prop.name
            for idx, val in enumerate(values):
                if idx == 0:
                    trace[prop.value] = val
                if val is not None:
                    indexed_prop = f"{prop_name}[{idx + 1}]"
                    if attributes.get(indexed_prop) is None:
                        attributes[indexed_prop] = val
    # marker selected_marker options
    __check_dict(trace, (_Chart_iprops.marker, _Chart_iprops.selected_marker, _Chart_iprops.options))
    axis = []
    traces: t.List[t.List[t.Optional[str]]] = []
    idx = 1
    indexed_trace = __get_multiple_indexed_attributes(attributes, _CHART_NAMES, idx)
    if len([x for x in indexed_trace if x]):
        while len([x for x in indexed_trace if x]):
            axis.append(
                __CHART_AXIS.get(
                    indexed_trace[_Chart_iprops.type.value] or trace[_Chart_iprops.type.value] or "",
                    __CHART_DEFAULT_AXIS,
                )
            )
            # marker selected_marker options
            __check_dict(indexed_trace, (_Chart_iprops.marker, _Chart_iprops.selected_marker, _Chart_iprops.options))
            if trace[_Chart_iprops.decimator.value] and not indexed_trace[_Chart_iprops.decimator.value]:
                # copy the decimator only once
                indexed_trace[_Chart_iprops.decimator.value] = trace[_Chart_iprops.decimator.value]
                trace[_Chart_iprops.decimator.value] = None
            traces.append([x or trace[i] for i, x in enumerate(indexed_trace)])
            idx += 1
            indexed_trace = __get_multiple_indexed_attributes(attributes, _CHART_NAMES, idx)
    else:
        traces.append(trace)
        # axis names
        axis.append(__CHART_AXIS.get(trace[_Chart_iprops.type.value] or "", __CHART_DEFAULT_AXIS))

    # list of data columns name indexes with label text
    dt_idx = tuple(e.value for e in (axis[0] + (_Chart_iprops.label, _Chart_iprops.text)))

    # configure columns
    columns: t.Set[str] = set()
    for j, trace in enumerate(traces):
        dt_idx = tuple(
            e.value for e in (axis[j] if j < len(axis) else axis[0]) + (_Chart_iprops.label, _Chart_iprops.text)
        )
        columns.update([trace[i] or "" for i in dt_idx if trace[i]])
    # add optionnal column if any
    markers = [
        t[_Chart_iprops.marker.value]
        or ({"color": t[_Chart_iprops.color.value]} if t[_Chart_iprops.color.value] else None)
        for t in traces
    ]
    opt_cols = set()
    for m in markers:
        if isinstance(m, (dict, _MapDict)):
            for prop1 in __CHART_MARKER_TO_COLS:
                val = m.get(prop1)
                if isinstance(val, str) and val not in columns:
                    opt_cols.add(val)

    # Validate the column names
    col_dict = _get_columns_dict(attributes.get("data"), list(columns), col_types, opt_columns=opt_cols)

    # Manage Decimator
    decimators: t.List[t.Optional[str]] = []
    for tr in traces:
        if tr[_Chart_iprops.decimator.value]:
            cls = gui._get_user_instance(
                class_name=str(tr[_Chart_iprops.decimator.value]), class_type=PropertyType.decimator.value
            )
            if isinstance(cls, PropertyType.decimator.value):
                decimators.append(str(tr[_Chart_iprops.decimator.value]))
                continue
        decimators.append(None)

    # set default columns if not defined
    icols = [[c2 for c2 in [__get_col_from_indexed(c1, i) for c1 in col_dict.keys()] if c2] for i in range(len(traces))]

    for i, tr in enumerate(traces):
        if i < len(axis):
            used_cols = {tr[ax.value] for ax in axis[i] if tr[ax.value]}
            unused_cols = [c for c in icols[i] if c not in used_cols]
            if unused_cols and not any(tr[ax.value] for ax in axis[i]):
                traces[i] = list(
                    v or (unused_cols.pop(0) if unused_cols and _Chart_iprops(j) in axis[i] else v)
                    for j, v in enumerate(tr)
                )

    if col_dict is not None:
        reverse_cols = {str(cd.get("dfid")): c for c, cd in col_dict.items()}

        # List used axis
        used_axis = [[e for e in (axis[j] if j < len(axis) else axis[0]) if tr[e.value]] for j, tr in enumerate(traces)]

        ret_dict = {
            "columns": col_dict,
            "labels": [
                reverse_cols.get(tr[_Chart_iprops.label.value] or "", (tr[_Chart_iprops.label.value] or ""))
                for tr in traces
            ],
            "texts": [
                reverse_cols.get(tr[_Chart_iprops.text.value] or "", (tr[_Chart_iprops.text.value] or None))
                for tr in traces
            ],
            "modes": [tr[_Chart_iprops.mode.value] for tr in traces],
            "types": [tr[_Chart_iprops.type.value] for tr in traces],
            "xaxis": [tr[_Chart_iprops.xaxis.value] for tr in traces],
            "yaxis": [tr[_Chart_iprops.yaxis.value] for tr in traces],
            "markers": markers,
            "selectedMarkers": [
                tr[_Chart_iprops.selected_marker.value]
                or (
                    {"color": tr[_Chart_iprops.selected_color.value]}
                    if tr[_Chart_iprops.selected_color.value]
                    else None
                )
                for tr in traces
            ],
            "traces": [
                [reverse_cols.get(c or "", c) for c in [tr[e.value] for e in used_axis[j]]]
                for j, tr in enumerate(traces)
            ],
            "orientations": [tr[_Chart_iprops.orientation.value] for tr in traces],
            "names": [tr[_Chart_iprops._name.value] for tr in traces],
            "lines": [
                tr[_Chart_iprops.line.value]
                if isinstance(tr[_Chart_iprops.line.value], (dict, _MapDict))
                else {"dash": tr[_Chart_iprops.line.value]}
                if tr[_Chart_iprops.line.value]
                else None
                for tr in traces
            ],
            "textAnchors": [tr[_Chart_iprops.text_anchor.value] for tr in traces],
            "options": [tr[_Chart_iprops.options.value] for tr in traces],
            "axisNames": [[e.name for e in ax] for ax in used_axis],
            "addIndex": [tr[_Chart_iprops.type.value] not in __CHART_NO_INDEX for tr in traces],
        }
        if len([d for d in decimators if d]):
            ret_dict.update(decimators=decimators)
        return ret_dict
    return {}
