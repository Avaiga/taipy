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

import re
import typing as t

from .._warnings import _warn
from .boolean import _is_boolean, _is_true
from .clientvarname import _to_camel_case


def _get_column_desc(columns: t.Dict[str, t.Any], key: str) -> t.Optional[t.Dict[str, t.Any]]:
    return next((x for x in columns.values() if x.get("dfid") == key), None)


def _get_name_indexed_property(attributes: t.Dict[str, t.Any], name: str) -> t.Dict[str, t.Any]:
    ret = {}
    index_re = re.compile(name + r"\[(.*)\]$")
    for key in attributes.keys():
        if m := index_re.match(key):
            ret[m.group(1)] = attributes.get(key)
    return ret


def _update_col_desc_from_indexed(
    attributes: t.Dict[str, t.Any], columns: t.Dict[str, t.Any], name: str, elt_name: str
):
    col_value = _get_name_indexed_property(attributes, name)
    for k, v in col_value.items():
        if col_desc := next((x for x in columns.values() if x.get("dfid") == k), None):
            if col_desc.get(_to_camel_case(name)) is None:
                col_desc[_to_camel_case(name)] = str(v)
        else:
            _warn(f"{elt_name}: '{k}' is not a displayed column in {name}[].")


def _enhance_columns(  # noqa: C901
    attributes: t.Dict[str, t.Any], hash_names: t.Dict[str, str], columns: t.Dict[str, t.Any], elt_name: str
):
    _update_col_desc_from_indexed(attributes, columns, "nan_value", elt_name)
    _update_col_desc_from_indexed(attributes, columns, "width", elt_name)
    filters = _get_name_indexed_property(attributes, "filter")
    for k, v in filters.items():
        if _is_true(v):
            if col_desc := _get_column_desc(columns, k):
                col_desc["filter"] = True
            else:
                _warn(f"{elt_name}: '{k}' is not a displayed column for filter[].")
    editables = _get_name_indexed_property(attributes, "editable")
    for k, v in editables.items():
        if _is_boolean(v):
            if col_desc := _get_column_desc(columns, k):
                col_desc["notEditable"] = not _is_true(v)
            else:
                _warn(f"{elt_name}: '{k}' is not a displayed column in editable[].")
    group_by = _get_name_indexed_property(attributes, "group_by")
    for k, v in group_by.items():
        if _is_true(v):
            if col_desc := _get_column_desc(columns, k):
                col_desc["groupBy"] = True
            else:
                _warn(f"{elt_name}: '{k}' is not a displayed column in group_by[].")
    apply = _get_name_indexed_property(attributes, "apply")
    for k, v in apply.items():  # pragma: no cover
        if col_desc := _get_column_desc(columns, k):
            if callable(v):
                value = hash_names.get(f"apply[{k}]")
            elif isinstance(v, str):
                value = v.strip()
            else:
                _warn(f"{elt_name}: invalid user or predefined function in apply[].")
                value = None
            if value:
                col_desc["apply"] = value
        else:
            _warn(f"{elt_name}: '{k}' is not a displayed column in apply[].")
    if _get_name_indexed_property(attributes, "style"):
        _warn("Table: property 'style[]' has been renamed to 'cell_class_name[]'.")
    cell_class_names = _get_name_indexed_property(attributes, "cell_class_name")
    for k, v in cell_class_names.items():  # pragma: no cover
        if col_desc := _get_column_desc(columns, k):
            if callable(v):
                value = hash_names.get(f"cell_class_name[{k}]")
            elif isinstance(v, str):
                value = v.strip()
            else:
                value = None
            if value in columns.keys():
                _warn(f"{elt_name}: cell_class_name[{k}] cannot be set to an column name '{value}'.")
            elif value:
                col_desc["className"] = value
        else:
            _warn(f"{elt_name}: '{k}' is not a displayed column in cell_class_name[].")
    tooltips = _get_name_indexed_property(attributes, "tooltip")
    for k, v in tooltips.items():  # pragma: no cover
        if col_desc := _get_column_desc(columns, k):
            if callable(v):
                value = hash_names.get(f"tooltip[{k}]")
            elif isinstance(v, str):
                value = v.strip()
            else:
                value = None
            if value in columns.keys():
                _warn(f"{elt_name}: tooltip[{k}] cannot be set to an column name '{value}'.")
            elif value:
                col_desc["tooltip"] = value
        else:
            _warn(f"{elt_name}: '{k}' is not a displayed column in tooltip[].")
    formats = _get_name_indexed_property(attributes, "format_fn")
    for k, v in formats.items():  # pragma: no cover
        if col_desc := _get_column_desc(columns, k):
            if callable(v):
                value = hash_names.get(f"format_fn[{k}]")
            elif isinstance(v, str):
                value = v.strip()
            else:
                value = None
            if value in columns.keys():
                _warn(f"{elt_name}: format_fn[{k}] cannot be set to an column name '{value}'.")
            elif value:
                col_desc["formatFn"] = value
        else:
            _warn(f"{elt_name}: '{k}' is not a displayed column in format_fn[].")
    editable = attributes.get("editable", False)
    loveable = _is_boolean(editable) and _is_true(editable)
    loves = _get_name_indexed_property(attributes, "lov")
    for k, v in loves.items():  # pragma: no cover
        col_desc = _get_column_desc(columns, k)
        if col_desc and (
            loveable
            or not col_desc.get("notEditable", True)
            or t.cast(str, col_desc.get("type", "")).startswith("bool")
        ):
            value = v.strip().split(";") if isinstance(v, str) else v  # type: ignore[assignment]
            if value is not None and not isinstance(value, (list, tuple)):
                _warn(f"{elt_name}: lov[{k}] should be a list.")
                value = None
            if value is not None:
                new_value = list(filter(lambda i: i is not None, value))
                if len(new_value) < len(value):
                    col_desc["freeLov"] = True
                    value = new_value
                col_desc["lov"] = value
        elif not col_desc:
            _warn(f"{elt_name}: '{k}' is not a displayed column in lov[].")
    return columns
