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

import re
import typing as t
import warnings

from ..types import NumberTypes
from ..utils import _RE_PD_TYPE, _get_date_col_str_name, _MapDict


def _add_to_dict_and_get(dico: t.Dict[str, t.Any], key: str, value: t.Any) -> t.Any:
    if key not in dico.keys():
        dico[key] = value
    return dico[key]


def _get_tuple_val(attr: tuple, index: int, default_val: t.Any) -> t.Any:
    return attr[index] if len(attr) > index else default_val


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
    if isinstance(columns, str):
        columns = [s.strip() for s in columns.split(";")]
    if isinstance(columns, (list, tuple)):
        coldict = {}
        idx = 0
        for col in columns:
            if col not in col_types_keys:
                warnings.warn(
                    f'Error column "{col}" is not present in the dataframe "{value.head(0) if hasattr(value, "head") else value}"'
                )
            else:
                coldict[col] = {"index": idx}
                idx += 1
        if opt_columns is not None:
            for col in opt_columns:
                if col in col_types_keys:
                    coldict[col] = {"index": idx}
                    idx += 1
        columns = coldict
    if isinstance(columns, _MapDict):
        columns = columns._dict
    if not isinstance(columns, dict):
        warnings.warn("Error: columns attributes should be a string, list, tuple or dict")
        columns = {}
    if len(columns) == 0:
        idx = 0
        for col in col_types_keys:
            columns[col] = {"index": idx}
            idx += 1
    idx = 0
    for col, ctype in col_types.items():
        col = str(col)
        if col in columns.keys():
            re_type = _RE_PD_TYPE.match(ctype)
            grps = re_type.groups() if re_type else ()
            ctype = grps[0] if grps else ctype
            columns[col]["type"] = ctype
            columns[col]["dfid"] = col
            if len(grps) > 4 and grps[4]:
                columns[col]["tz"] = grps[4]
            idx = _add_to_dict_and_get(columns[col], "index", idx) + 1
            if ctype == "datetime":
                if date_format:
                    _add_to_dict_and_get(columns[col], "format", date_format)
                columns[_get_date_col_str_name(col_types.keys(), col)] = columns.pop(col)  # type: ignore
            elif number_format and ctype in NumberTypes:
                _add_to_dict_and_get(columns[col], "format", number_format)
    return columns


__RE_INDEXED_DATA = re.compile(r"^(\d+)\/(.*)")


def _get_col_from_indexed(col_name: str, idx: int) -> t.Optional[str]:
    if re_res := __RE_INDEXED_DATA.search(col_name):
        return col_name if str(idx) == re_res.group(1) else None
    return col_name


def _get_idx_from_col(col_name) -> int:
    if re_res := __RE_INDEXED_DATA.search(col_name):
        return int(re_res.group(1))
    return 0


def _to_camel_case(value: str, upcase_first=False) -> str:
    if not isinstance(value, str):
        raise Exception("_to_camel_case allows only string parameter")

    if len(value) <= 1:
        return value.lower()
    value = value.replace("_", " ").title().replace(" ", "").replace("[", "_").replace("]", "_")
    return value[0].lower() + value[1:] if not upcase_first else value
