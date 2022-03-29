import re
import typing as t
import warnings

from ..types import NumberTypes
from ..utils import _get_date_col_str_name, _MapDict


def _add_to_dict_and_get(dico: t.Dict[str, t.Any], key: str, value: t.Any) -> t.Any:
    if key not in dico.keys():
        dico[key] = value
    return dico[key]


def _get_tuple_val(attr: tuple, index: int, default_val: t.Any) -> t.Any:
    return attr[index] if len(attr) > index else default_val


def _get_columns_dict(
    value: t.Any,
    columns: t.Union[str, t.List[str], t.Tuple[str], t.Dict[str, t.Any], _MapDict],
    col_types: t.Optional[t.Dict[str, str]] = None,
    date_format: t.Optional[str] = None,
    number_format: t.Optional[str] = None,
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
    for col, type in col_types.items():
        col = str(col)
        if col in columns.keys():
            columns[col]["type"] = type
            columns[col]["dfid"] = col
            idx = _add_to_dict_and_get(columns[col], "index", idx) + 1
            if type.startswith("datetime64"):
                if date_format:
                    _add_to_dict_and_get(columns[col], "format", date_format)
                columns[_get_date_col_str_name(col_types.keys(), col)] = columns.pop(col)  # type: ignore
            elif number_format and type in NumberTypes:
                _add_to_dict_and_get(columns[col], "format", number_format)
    return columns


_indexed_data = re.compile(r"^(\d+)\/(.*)")


def _get_col_from_indexed(col_name: str, idx: int) -> t.Optional[str]:
    if re_res := _indexed_data.search(col_name):
        return col_name if str(idx) == re_res.group(1) else None
    return col_name


def _get_idx_from_col(col_name) -> int:
    if re_res := _indexed_data.search(col_name):
        return int(re_res.group(1))
    return 0


def _to_camel_case(value: str) -> str:
    if not isinstance(value, str):
        raise Exception("_to_camel_case allows only string parameter")

    if len(value) <= 1:
        return value.lower()
    value = value.replace("_", " ").title().replace(" ", "").replace("[", "_").replace("]", "_")
    return value[0].lower() + value[1:]
