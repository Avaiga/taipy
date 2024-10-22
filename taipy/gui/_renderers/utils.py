# Copyright 2021-2024 Avaiga Private Limited
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
import typing as t
from pathlib import Path

import pandas as pd
from watchdog.events import FileSystemEventHandler

from taipy.common.logger._taipy_logger import _TaipyLogger

from .._warnings import _warn
from ..types import NumberTypes
from ..utils import _RE_PD_TYPE, _get_date_col_str_name, _MapDict

if t.TYPE_CHECKING:
    from . import _Renderer


def _add_to_dict_and_get(dico: t.Dict[str, t.Any], key: str, value: t.Any) -> t.Any:
    if key not in dico.keys():
        dico[key] = value
    return dico[key]


def _get_tuple_val(attr: tuple, index: int, default_val: t.Any) -> t.Any:
    return attr[index] if len(attr) > index else default_val


def _get_columns_dict_from_list(
    col_list: t.Union[t.List[str], t.Tuple[str]], col_types_keys: t.List[str], value: t.Any
):
    col_dict = {}
    idx = 0
    cols = None

    for col in col_list:
        if col in col_types_keys:
            col_dict[col] = {"index": idx}
            idx += 1
        elif col:
            if cols is None:
                cols = (
                    list(value.columns)
                    if isinstance(value, pd.DataFrame)
                    else list(value.keys())
                    if isinstance(value, (dict, _MapDict))
                    else value
                    if isinstance(value, (list, tuple))
                    else []
                )

            if cols and (col not in cols):
                _warn(
                    f'Column "{col}" is not present. Available columns: {cols}.'  # noqa: E501
                )
            else:
                _warn(
                    "The 'data' property value is of an unsupported type."
                    + " Only DataFrame, dict, list, or tuple are supported."
                )
    return col_dict


def _get_columns_dict(  # noqa: C901
    value: t.Any,
    columns: t.Union[str, t.List[str], t.Tuple[str], t.Dict[str, t.Any], _MapDict],
    col_types: t.Optional[t.Dict[str, str]] = None,
    date_format: t.Optional[str] = None,
    number_format: t.Optional[str] = None,
    opt_columns: t.Optional[t.Set[str]] = None,
):
    if col_types is None:
        return None
    col_types_keys = [str(c) for c in col_types.keys()]
    col_dict: t.Optional[dict] = None
    if isinstance(columns, str):
        col_dict = _get_columns_dict_from_list([s.strip() for s in columns.split(";")], col_types_keys, value)
    elif isinstance(columns, (list, tuple)):
        col_dict = _get_columns_dict_from_list(columns, col_types_keys, value)  # type: ignore[arg-type]
    elif isinstance(columns, _MapDict):
        col_dict = columns._dict.copy()
    elif isinstance(columns, dict):
        col_dict = columns.copy()
    if not isinstance(col_dict, dict):
        _warn("Error: columns attributes should be a string, a list, a tuple or a dict.")
        col_dict = {}
    nb_cols = len(col_dict)
    if nb_cols == 0:
        for col in col_types_keys:
            col_dict[col] = {"index": nb_cols}
            nb_cols += 1
    else:
        col_dict = {str(k): v for k, v in col_dict.items()}
        if opt_columns:
            for col in opt_columns:
                if col in col_types_keys and col not in col_dict:
                    col_dict[col] = {"index": nb_cols}
                    nb_cols += 1
    idx = 0
    for col, ctype in col_types.items():
        col = str(col)
        if col in col_dict:
            re_type = _RE_PD_TYPE.match(ctype)
            grps = re_type.groups() if re_type else ()
            ctype = grps[0] if grps else ctype
            col_dict[col]["type"] = ctype
            col_dict[col]["dfid"] = col
            if len(grps) > 4 and grps[4]:
                col_dict[col]["tz"] = grps[4]
            idx = _add_to_dict_and_get(col_dict[col], "index", idx) + 1
            if ctype == "datetime":
                if date_format:
                    _add_to_dict_and_get(col_dict[col], "format", date_format)
                col_dict[_get_date_col_str_name(col_types.keys(), col)] = col_dict.pop(col)  # type: ignore
            elif number_format and ctype in NumberTypes:
                _add_to_dict_and_get(col_dict[col], "format", number_format)
    return col_dict


class FileWatchdogHandler(FileSystemEventHandler):
    def __init__(self, file_path: str, renderer: "_Renderer") -> None:
        self._file_path = file_path
        self._renderer = renderer
        self._last_modified = datetime.datetime.now()

    def on_modified(self, event):
        if datetime.datetime.now() - self._last_modified < datetime.timedelta(seconds=1):
            return
        self._last_modified = datetime.datetime.now()
        if Path(event.src_path).resolve() == Path(self._file_path).resolve():
            self._renderer.set_content(self._file_path)
            _TaipyLogger._get_logger().info(f"File '{self._file_path}' has been modified.")
