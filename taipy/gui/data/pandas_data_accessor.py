import warnings
import typing as t

import pandas as pd

from ..utils import _get_dict_value, _get_date_col_str_name
from .data_accessor import DataAccessor


class PandasDataAccessor(DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.Callable:
        return pd.DataFrame

    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        if isinstance(value, pd.DataFrame):
            warnings.warn("Error: cannot update value for dataframe: " + var_name)
            return None
        return value

    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return isinstance(value, pd.DataFrame)

    def get_data(self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:  # noqa: C901
        ret_payload = {}
        if isinstance(value, pd.DataFrame):
            paged = not _get_dict_value(payload, "alldata")
            if paged:
                keys = payload.keys()
                ret_payload["pagekey"] = payload["pagekey"] if "pagekey" in keys else "unknown page"
                if "infinite" in keys:
                    ret_payload["infinite"] = payload["infinite"]
            else:
                ret_payload["alldata"] = payload["alldata"]
            # deal with columns
            cols = _get_dict_value(payload, "columns")
            if isinstance(cols, list) and len(cols):
                col_types = value.dtypes[value.dtypes.index.isin(cols)]
            else:
                col_types = value.dtypes
            cols = col_types.index.tolist()
            # deal with dates
            datecols = col_types[col_types.astype("string").str.startswith("datetime")].index.tolist()
            if len(datecols) != 0:
                # copy the df so that we don't "mess" with the user's data
                value = value.copy()
                for col in datecols:
                    newcol = _get_date_col_str_name(cols, col)
                    cols.append(newcol)
                    value[newcol] = value[col].dt.strftime(DataAccessor._WS_DATE_FORMAT).astype("string")
                # remove the date columns from the list of columns
                cols = list(set(cols) - set(datecols))
            if paged:
                rowcount = len(value)
                # here we'll deal with start and end values from payload if present
                if isinstance(payload["start"], int):
                    start = int(payload["start"])
                else:
                    try:
                        start = int(str(payload["start"]), base=10)
                    except Exception:
                        warnings.warn(f'start should be an int value {payload["start"]}')
                        start = 0
                if isinstance(payload["end"], int):
                    end = int(payload["end"])
                else:
                    try:
                        end = int(str(payload["end"]), base=10)
                    except Exception:
                        end = -1
                if start < 0 or start >= rowcount:
                    start = 0
                if end < 0 or end >= rowcount:
                    end = rowcount - 1
                # deal with sort
                order_by = _get_dict_value(payload, "orderby")
                if isinstance(order_by, str) and len(order_by):
                    new_indexes = value[order_by].values.argsort(axis=0)
                    if _get_dict_value(payload, "sort") == "desc":
                        # reverse order
                        new_indexes = new_indexes[::-1]
                    new_indexes = new_indexes[slice(start, end + 1)]
                else:
                    new_indexes = slice(start, end + 1)
                value = value.loc[:, cols].iloc[new_indexes]  # returns a view
                dictret = {"data": value.to_dict(orient="records"), "rowcount": rowcount, "start": start}
                value = dictret
            if not paged:
                # view with the requested columns
                value = value.loc[:, cols].to_dict(orient="list")
            ret_payload["value"] = value
        return ret_payload

    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        if isinstance(value, pd.DataFrame):
            return value.dtypes.apply(lambda x: x.name).to_dict()
        return None
