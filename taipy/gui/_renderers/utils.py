# Copyright 2021-2025 Avaiga Private Limited
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
    col_list: t.Union[t.List[str], t.Tuple[str]], cols_description: t.Dict[str, t.Dict[str, str]]
):
    col_dict: t.Dict[str, t.Dict[str, t.Any]] = {}
    idx = 0
    for col in col_list:
        if col in cols_description:
            col_dict[col] = cols_description[col].copy()
            col_dict[col]["index"] = idx
            idx += 1
        elif col and col not in cols_description:
            _warn(f'Column "{col}" is not present. Available columns: {list(cols_description)}.')
    return col_dict


def _get_columns_dict(  # noqa: C901
    columns: t.Union[str, t.List[str], t.Tuple[str], t.Dict[str, t.Any], _MapDict],
    cols_description: t.Optional[t.Dict[str, t.Dict[str, str]]] = None,
    date_format: t.Optional[str] = None,
    number_format: t.Optional[str] = None,
    opt_columns: t.Optional[t.Set[str]] = None,
):
    if cols_description is None:
        return None
    col_types_keys = [str(c) for c in cols_description.keys()]
    col_dict: t.Optional[dict] = None
    if isinstance(columns, str):
        col_dict = _get_columns_dict_from_list([s.strip() for s in columns.split(";")], cols_description)
    elif isinstance(columns, (list, tuple)):
        col_dict = _get_columns_dict_from_list(columns, cols_description)
    elif isinstance(columns, _MapDict):
        col_dict = columns._dict.copy()
    elif isinstance(columns, dict):
        col_dict = columns.copy()
    if not isinstance(col_dict, dict):
        _warn("Error: columns attributes should be a string, a list, a tuple or a dict.")
        col_dict = {}
    nb_cols = len(col_dict)
    if nb_cols == 0:
        for col in cols_description:
            col_dict[str(col)] = {"index": nb_cols}
            nb_cols += 1
    else:
        col_dict = {str(k): v for k, v in col_dict.items()}
        if opt_columns:
            for col in opt_columns:
                if col in col_types_keys and col not in col_dict:
                    col_dict[col] = {"index": nb_cols}
                    nb_cols += 1
    idx = 0
    for col, col_description in cols_description.items():
        col = str(col)
        if col in col_dict:
            col_type = col_description.get("type", "")
            re_type = _RE_PD_TYPE.match(col_type)
            groups = re_type.groups() if re_type else ()
            col_type = groups[0] if groups else col_type
            if len(groups) > 4 and groups[4]:
                col_dict[col]["tz"] = groups[4]
            old_col = None
            if col_type == "datetime":
                if date_format:
                    _add_to_dict_and_get(col_dict[col], "format", date_format)
                old_col = col
                col = _get_date_col_str_name(cols_description.keys(), col)
                col_dict[col] = col_dict.pop(old_col)
            elif number_format and col_type in NumberTypes:
                _add_to_dict_and_get(col_dict[col], "format", number_format)
            if "index" not in col_dict[col]:
                col_dict[col]["index"] = idx
            idx += 1
            col_dict[col]["type"] = col_type
            col_dict[col]["dfid"] = old_col or col
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
