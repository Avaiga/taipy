import typing as t
import warnings
from importlib import util

import numpy as np
import pandas as pd

from ..gui import Gui
from ..utils import _get_date_col_str_name
from .data_accessor import _DataAccessor
from .data_format import _DataFormat

_has_arrow_module = False
if util.find_spec("pyarrow"):
    _has_arrow_module = True
    import pyarrow as pa


class _PandasDataAccessor(_DataAccessor):

    __types = (pd.DataFrame,)

    @staticmethod
    def get_supported_classes() -> t.List[str]:
        return [t.__name__ for t in _PandasDataAccessor.__types]

    @staticmethod
    def __style_function(
        row: pd.Series, gui: Gui, column_name: t.Optional[str], user_function: t.Callable, function_name: str
    ) -> str:  # pragma: no cover
        args = []
        if column_name:
            args.append(row[column_name])
        args.extend((row.name, row))
        if column_name:
            args.append(column_name)
        try:
            return str(gui._call_function_with_state(user_function, args))
        except Exception as e:
            warnings.warn(f"Exception raised when calling user style function {function_name}\n{e}")
        return ""

    def __build_transferred_cols(
        self, gui: Gui, payload_cols: t.Any, data: pd.DataFrame, styles: t.Optional[t.Dict[str, str]] = None
    ) -> pd.DataFrame:
        if isinstance(payload_cols, list) and len(payload_cols):
            col_types = data.dtypes[data.dtypes.index.astype(str).isin(payload_cols)]
        else:
            col_types = data.dtypes
        cols = col_types.index.astype(str).tolist()
        is_copied = False
        if styles:
            # copy the df so that we don't "mess" with the user's data
            data = data.copy()
            is_copied = True
            for k, v in styles.items():
                applied = False
                func = gui._get_user_function(v)
                if callable(func):
                    applied = self.__apply_user_function(gui, func, k if k in cols else None, v, data)
                if not applied:
                    data[v] = v
                cols.append(v)
        # deal with dates
        datecols = col_types[col_types.astype(str).str.startswith("datetime")].index.tolist()
        if len(datecols) != 0:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                data = data.copy()
            for col in datecols:
                newcol = _get_date_col_str_name(cols, col)
                cols.append(newcol)
                data[newcol] = data[col].dt.strftime(_DataAccessor._WS_DATE_FORMAT).astype(str)
            # remove the date columns from the list of columns
            cols = list(set(cols) - set(datecols))
        data = data.loc[:, data.dtypes[data.dtypes.index.astype(str).isin(cols)].index]
        return data

    def __apply_user_function(
        self, gui: Gui, user_function: t.Callable, column_name: t.Optional[str], function_name: str, data: pd.DataFrame
    ):
        arg_count = user_function.__code__.co_argcount
        if arg_count > 1:
            data[function_name] = data.apply(
                _PandasDataAccessor.__style_function,
                axis=1,
                args=(gui, column_name, user_function, function_name),
            )
            return True
        else:
            warnings.warn(f"Style function {function_name} should take at least a value as second argument")
        return False

    def __format_data(
        self,
        data: pd.DataFrame,
        data_format: _DataFormat,
        orient: str,
        start: t.Optional[int] = None,
        rowcount: t.Optional[int] = None,
        data_extraction: t.Optional[bool] = None,
        handle_nan: t.Optional[bool] = False,
    ) -> t.Dict[str, t.Any]:
        ret: t.Dict[str, t.Any] = {
            "format": str(data_format.value),
        }
        if rowcount is not None:
            ret["rowcount"] = rowcount
        if start is not None:
            ret["start"] = start
        if data_extraction is not None:
            ret["dataExtraction"] = data_extraction  # Extract data out of dictionary on frontend
        if data_format == _DataFormat.APACHE_ARROW and _has_arrow_module:
            # Convert from pandas to Arrow
            table = pa.Table.from_pandas(data)
            # Create sink buffer stream
            sink = pa.BufferOutputStream()
            # Create Stream writer
            writer = pa.ipc.new_stream(sink, table.schema)
            # Write data to table
            writer.write_table(table)
            writer.close()
            # end buffer stream
            buf = sink.getvalue()
            # convert buffer to python bytes and return
            ret["data"] = buf.to_pybytes()
            ret["orient"] = orient
        elif data_format == _DataFormat.APACHE_ARROW:
            raise RuntimeError("Cannot use Arrow as pyarrow package is not installed")
        else:
            # workaround for python built in json encoder that does not yet support ignore_nan
            ret["data"] = data.replace([np.nan], ["NaN" if handle_nan else None]).to_dict(orient=orient)  # type: ignore
        return ret

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, _PandasDataAccessor.__types):
            return value.dtypes.apply(lambda x: x.name).to_dict()
        elif isinstance(value, list):
            ret_dict: t.Dict[str, str] = {}
            for i, v in enumerate(value):
                ret_dict.update({f"{i}/{k}": v for k, v in v.dtypes.apply(lambda x: x.name).items()})
            return ret_dict
        return None

    def __get_data(  # noqa: C901
        self,
        gui: Gui,
        var_name: str,
        value: pd.DataFrame,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
        col_prefix: t.Optional[str] = "",
    ) -> t.Dict[str, t.Any]:
        columns = payload.get("columns", [])
        if col_prefix:
            columns = [c.removeprefix(col_prefix) for c in columns]
        ret_payload = {"pagekey": payload.get("pagekey", "unknown page")}
        paged = not payload.get("alldata", False)
        if paged:
            aggregates = payload.get("aggregates")
            applies = payload.get("applies")
            if isinstance(aggregates, list) and len(aggregates) and isinstance(applies, dict):
                applies_with_fn = {
                    k: v if v in gui._aggregate_functions else gui._get_user_function(v) for k, v in applies.items()
                }

                for col in columns:
                    if col not in applies_with_fn.keys():
                        applies_with_fn[col] = "first"
                try:
                    value = value.groupby(aggregates).agg(applies_with_fn)
                except Exception:
                    warnings.warn(f"Cannot aggregate {var_name} with groupby {aggregates} and aggregates {applies}")
            inf = payload.get("infinite")
            if inf is not None:
                ret_payload["infinite"] = inf
            # real number of rows is needed to calculate the number of pages
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
            order_by = payload.get("orderby")
            if isinstance(order_by, str) and len(order_by):
                new_indexes = value[order_by].values.argsort(axis=0)
                if payload.get("sort") == "desc":
                    # reverse order
                    new_indexes = new_indexes[::-1]
                new_indexes = new_indexes[slice(start, end + 1)]
            else:
                new_indexes = slice(start, end + 1)  # type: ignore
            value = self.__build_transferred_cols(gui, columns, value.iloc[new_indexes], styles=payload.get("styles"))
            dictret = self.__format_data(
                value, data_format, "records", start, rowcount, handle_nan=payload.get("handlenan", False)
            )
        else:
            ret_payload["alldata"] = True
            nb_rows_max = payload.get("width")
            # view with the requested columns
            if nb_rows_max and nb_rows_max < len(value) / 2:
                value = value.copy()
                value["tp_index"] = value.index
                # we need to be more clever than this :-)
                value = value.iloc[:: (len(value) // nb_rows_max)]
            value = self.__build_transferred_cols(gui, columns, value)
            dictret = self.__format_data(value, data_format, "list", data_extraction=True)
        ret_payload["value"] = dictret
        return ret_payload

    def get_data(
        self, gui: Gui, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        if isinstance(value, list):
            is_chart = payload.get("alldata", False)
            if is_chart:
                ret_payload = {
                    "alldata": True,
                    "value": {"multi": True},
                    "pagekey": payload.get("pagekey", "unknown page"),
                }
                data = []
                for i, v in enumerate(value):
                    ret = (
                        self.__get_data(gui, var_name, v, payload, data_format, f"{i}/")
                        if isinstance(v, pd.DataFrame)
                        else {}
                    )
                    ret_val = ret.get("value", {})
                    data.append(ret_val.pop("data", None))
                    ret_payload.get("value", {}).update(ret_val)
                ret_payload["value"]["data"] = data
                return ret_payload
            else:
                value = value[0]
        if isinstance(value, _PandasDataAccessor.__types):
            return self.__get_data(gui, var_name, value, payload, data_format)
        return {}
