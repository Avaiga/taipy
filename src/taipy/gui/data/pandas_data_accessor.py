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

import typing as t
from datetime import datetime
from importlib import util

import numpy as np
import pandas as pd

from .._warnings import _warn
from ..gui import Gui
from ..types import PropertyType
from ..utils import _RE_PD_TYPE, _get_date_col_str_name
from .data_accessor import _DataAccessor
from .data_format import _DataFormat
from .utils import _df_data_filter, _df_relayout

_has_arrow_module = False
if util.find_spec("pyarrow"):
    _has_arrow_module = True
    import pyarrow as pa


class _PandasDataAccessor(_DataAccessor):
    __types = (pd.DataFrame,)

    __INDEX_COL = "_tp_index"

    __AGGREGATE_FUNCTIONS: t.List[str] = ["count", "sum", "mean", "median", "min", "max", "std", "first", "last"]

    @staticmethod
    def get_supported_classes() -> t.List[str]:
        return [t.__name__ for t in _PandasDataAccessor.__types]  # type: ignore

    @staticmethod
    def __user_function(
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
            _warn(f"Exception raised when calling user function {function_name}()", e)
        return ""

    def __is_date_column(self, data: pd.DataFrame, col_name: str) -> bool:
        col_types = data.dtypes[data.dtypes.index.astype(str) == col_name]
        return len(col_types[col_types.astype(str).str.startswith("datetime")]) > 0  # type: ignore

    def __build_transferred_cols(
        self,
        gui: Gui,
        payload_cols: t.Any,
        dataframe: pd.DataFrame,
        styles: t.Optional[t.Dict[str, str]] = None,
        tooltips: t.Optional[t.Dict[str, str]] = None,
        is_copied: t.Optional[bool] = False,
        new_indexes: t.Optional[np.ndarray] = None,
        handle_nan: t.Optional[bool] = False,
    ) -> pd.DataFrame:
        if isinstance(payload_cols, list) and len(payload_cols):
            col_types = dataframe.dtypes[dataframe.dtypes.index.astype(str).isin(payload_cols)]
        else:
            col_types = dataframe.dtypes
        cols = col_types.index.astype(str).tolist()
        if styles:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                dataframe = dataframe.copy()
                is_copied = True
            for k, v in styles.items():
                col_applied = False
                func = gui._get_user_function(v)
                if callable(func):
                    col_applied = self.__apply_user_function(gui, func, k if k in cols else None, v, dataframe, "tps__")
                if not col_applied:
                    dataframe[v] = v
                cols.append(col_applied or v)
        if tooltips:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                dataframe = dataframe.copy()
                is_copied = True
            for k, v in tooltips.items():
                col_applied = False
                func = gui._get_user_function(v)
                if callable(func):
                    col_applied = self.__apply_user_function(gui, func, k if k in cols else None, v, dataframe, "tpt__")
                cols.append(col_applied or v)
        # deal with dates
        datecols = col_types[col_types.astype(str).str.startswith("datetime")].index.tolist()  # type: ignore
        if len(datecols) != 0:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                dataframe = dataframe.copy()
            tz = Gui._get_timezone()
            for col in datecols:
                newcol = _get_date_col_str_name(cols, col)
                cols.append(newcol)
                re_type = _RE_PD_TYPE.match(str(col_types[col]))
                grps = re_type.groups() if re_type else ()
                if len(grps) > 4 and grps[4]:
                    dataframe[newcol] = (
                        dataframe[col]
                        .dt.tz_convert("UTC")
                        .dt.strftime(_DataAccessor._WS_DATE_FORMAT)
                        .astype(str)
                        .replace("nan", "NaT" if handle_nan else None)
                    )
                else:
                    dataframe[newcol] = (
                        dataframe[col]
                        .dt.tz_localize(tz)
                        .dt.tz_convert("UTC")
                        .dt.strftime(_DataAccessor._WS_DATE_FORMAT)
                        .astype(str)
                        .replace("nan", "NaT" if handle_nan else None)
                    )

            # remove the date columns from the list of columns
            cols = list(set(cols) - set(datecols))
        dataframe = dataframe.iloc[new_indexes] if new_indexes is not None else dataframe
        dataframe = dataframe.loc[:, dataframe.dtypes[dataframe.dtypes.index.astype(str).isin(cols)].index]  # type: ignore
        return dataframe

    def __apply_user_function(
        self,
        gui: Gui,
        user_function: t.Callable,
        column_name: t.Optional[str],
        function_name: str,
        data: pd.DataFrame,
        prefix: t.Optional[str],
    ):
        try:
            new_col_name = f"{prefix}{column_name}__{function_name}" if column_name else function_name
            data[new_col_name] = data.apply(
                _PandasDataAccessor.__user_function,
                axis=1,
                args=(gui, column_name, user_function, function_name),
            )
            return new_col_name
        except Exception as e:
            _warn(f"Exception raised when invoking user function {function_name}()", e)
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
            ret["dataExtraction"] = data_extraction  # Extract data out of dictionary on front-end
        if data_format == _DataFormat.APACHE_ARROW:
            if not _has_arrow_module:
                raise RuntimeError("Cannot use Arrow as pyarrow package is not installed")
            # Convert from pandas to Arrow
            table = pa.Table.from_pandas(data)
            # Create sink buffer stream
            sink = pa.BufferOutputStream()
            # Create Stream writer
            writer = pa.ipc.new_stream(sink, table.schema)
            # Write data to table
            writer.write_table(table)
            writer.close()
            # End buffer stream
            buf = sink.getvalue()
            # Convert buffer to Python bytes and return
            ret["data"] = buf.to_pybytes()
            ret["orient"] = orient
        else:
            # Workaround for Python built in JSON encoder that does not yet support ignore_nan
            ret["data"] = data.replace([np.nan, pd.NA], [None, None]).to_dict(orient=orient)  # type: ignore
        return ret

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, _PandasDataAccessor.__types):  # type: ignore
            return {str(k): v for k, v in value.dtypes.apply(lambda x: x.name.lower()).items()}
        elif isinstance(value, list):
            ret_dict: t.Dict[str, str] = {}
            for i, v in enumerate(value):
                ret_dict.update({f"{i}/{k}": v for k, v in v.dtypes.apply(lambda x: x.name.lower()).items()})
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
            columns = [c[len(col_prefix) :] if c.startswith(col_prefix) else c for c in columns]
        ret_payload = {"pagekey": payload.get("pagekey", "unknown page")}
        paged = not payload.get("alldata", False)
        is_copied = False

        # add index if not chart
        if paged:
            if _PandasDataAccessor.__INDEX_COL not in value.columns:
                value = value.copy()
                is_copied = True
                value[_PandasDataAccessor.__INDEX_COL] = value.index
            if columns and _PandasDataAccessor.__INDEX_COL not in columns:
                columns.append(_PandasDataAccessor.__INDEX_COL)

        # filtering
        filters = payload.get("filters")
        if isinstance(filters, list) and len(filters) > 0:
            query = ""
            vars = []
            for fd in filters:
                col = fd.get("col")
                val = fd.get("value")
                action = fd.get("action")
                if isinstance(val, str):
                    if self.__is_date_column(value, col):
                        val = datetime.fromisoformat(val[:-1])
                    vars.append(val)
                val = f"@vars[{len(vars) - 1}]" if isinstance(val, (str, datetime)) else val
                right = f".str.contains({val})" if action == "contains" else f" {action} {val}"
                if query:
                    query += " and "
                query += f"`{col}`{right}"
            try:
                value = value.query(query)
                is_copied = True
            except Exception as e:
                _warn(f"Dataframe filtering: invalid query '{query}' on {value.head()}", e)

        if paged:
            aggregates = payload.get("aggregates")
            applies = payload.get("applies")
            if isinstance(aggregates, list) and len(aggregates) and isinstance(applies, dict):
                applies_with_fn = {
                    k: v if v in _PandasDataAccessor.__AGGREGATE_FUNCTIONS else gui._get_user_function(v)
                    for k, v in applies.items()
                }

                for col in columns:
                    if col not in applies_with_fn.keys():
                        applies_with_fn[col] = "first"
                try:
                    value = value.groupby(aggregates).agg(applies_with_fn)
                except Exception:
                    _warn(f"Cannot aggregate {var_name} with groupby {aggregates} and aggregates {applies}.")
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
                    _warn(f'start should be an int value {payload["start"]}.')
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
                try:
                    if value.columns.dtype.name == "int64":
                        order_by = int(order_by)
                    new_indexes = value[order_by].values.argsort(axis=0)
                    if payload.get("sort") == "desc":
                        # reverse order
                        new_indexes = new_indexes[::-1]
                    new_indexes = new_indexes[slice(start, end + 1)]
                except Exception:
                    _warn(f"Cannot sort {var_name} on columns {order_by}.")
                    new_indexes = slice(start, end + 1)  # type: ignore
            else:
                new_indexes = slice(start, end + 1)  # type: ignore
            value = self.__build_transferred_cols(
                gui,
                columns,
                value,
                styles=payload.get("styles"),
                tooltips=payload.get("tooltips"),
                is_copied=is_copied,
                new_indexes=new_indexes,
                handle_nan=payload.get("handlenan", False),
            )
            dictret = self.__format_data(
                value, data_format, "records", start, rowcount, handle_nan=payload.get("handlenan", False)
            )
        else:
            ret_payload["alldata"] = True
            decimator_payload: t.Dict[str, t.Any] = payload.get("decimatorPayload", {})
            decimators = decimator_payload.get("decimators", [])
            nb_rows_max = decimator_payload.get("width")
            for decimator_pl in decimators:
                decimator = decimator_pl.get("decimator")
                decimator_instance = (
                    gui._get_user_instance(decimator, PropertyType.decimator.value) if decimator is not None else None
                )
                if isinstance(decimator_instance, PropertyType.decimator.value):
                    x_column, y_column, z_column = (
                        decimator_pl.get("xAxis", ""),
                        decimator_pl.get("yAxis", ""),
                        decimator_pl.get("zAxis", ""),
                    )
                    chart_mode = decimator_pl.get("chartMode", "")
                    if decimator_instance._zoom and "relayoutData" in decimator_payload and not z_column:
                        relayoutData = decimator_payload.get("relayoutData", {})
                        x0 = relayoutData.get("xaxis.range[0]")
                        x1 = relayoutData.get("xaxis.range[1]")
                        y0 = relayoutData.get("yaxis.range[0]")
                        y1 = relayoutData.get("yaxis.range[1]")

                        value, is_copied = _df_relayout(
                            value, x_column, y_column, chart_mode, x0, x1, y0, y1, is_copied
                        )

                    if nb_rows_max and decimator_instance._is_applicable(value, nb_rows_max, chart_mode):
                        try:
                            value, is_copied = _df_data_filter(
                                value,
                                x_column,
                                y_column,
                                z_column,
                                decimator=decimator_instance,
                                payload=decimator_payload,
                                is_copied=is_copied,
                            )
                            gui._call_on_change(f"{var_name}.{decimator}.nb_rows", len(value))
                        except Exception as e:
                            _warn(f"Limit rows error with {decimator} for Dataframe", e)
            value = self.__build_transferred_cols(gui, columns, value, is_copied=is_copied)
            dictret = self.__format_data(value, data_format, "list", data_extraction=True)
        ret_payload["value"] = dictret
        return ret_payload

    def get_data(
        self, gui: Gui, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        if isinstance(value, list):
            # If is_chart data
            if payload.get("alldata", False):
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
        if isinstance(value, _PandasDataAccessor.__types):  # type: ignore
            return self.__get_data(gui, var_name, value, payload, data_format)
        return {}
