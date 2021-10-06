import pandas as pd
import warnings

from ..utils import _MapDictionary, get_date_col_str_name


def _add_to_dict_and_get(dico, key, value):
    if key not in dico.keys():
        dico[key] = value
    return dico[key]


def _get_columns_dict(value, columns, date_format="MM/dd/yyyy"):
    if isinstance(value, pd.DataFrame):
        coltypes = value.dtypes.apply(lambda x: x.name).to_dict()
        if isinstance(columns, str):
            columns = [s.strip() for s in columns.split(";")]
        if isinstance(columns, (list, tuple)):
            coldict = {}
            idx = 0
            for col in columns:
                if col not in coltypes.keys():
                    warnings.warn(f'Error column "{col}" is not present in the dataframe "{value.head(0)}"')
                else:
                    coldict[col] = {"index": idx}
                    idx += 1
            columns = coldict
        if isinstance(columns, _MapDictionary):
            columns = columns._dict
        if not isinstance(columns, dict):
            warnings.warn("Error: columns attributes should be a string, list, tuple or dict")
            columns = {}
        if len(columns) == 0:
            idx = 0
            for col in coltypes.keys():
                columns[col] = {"index": idx}
                idx += 1
        idx = 0
        for col, type in coltypes.items():
            if col in columns.keys():
                columns[col]["type"] = type
                columns[col]["dfid"] = col
                idx = _add_to_dict_and_get(columns[col], "index", idx) + 1
                if type.startswith("datetime64"):
                    _add_to_dict_and_get(columns[col], "format", date_format)
                    columns[get_date_col_str_name(value, col)] = columns.pop(col)
    return columns


def _to_camel_case(value):
    if not isinstance(value, str):
        raise Exception("_to_camel_case allows only string parameter")

    if len(value) <= 1:
        return value.lower()
    value = value.replace("_", " ").title().replace(" ", "")
    return value[0].lower() + value[1:]
