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

import os
import typing as t
from datetime import datetime
from importlib import util
from tempfile import mkstemp

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .._warnings import _warn
from ..gui import Gui
from ..types import PropertyType
from ..utils import _RE_PD_TYPE, _get_date_col_str_name
from .comparison import _compare_function
from .data_accessor import _DataAccessor
from .data_format import _DataFormat
from .utils import _df_data_filter, _df_relayout

_has_arrow_module = False
if util.find_spec("pyarrow"):
    _has_arrow_module = True
    import pyarrow as pa


class _PandasDataAccessor(_DataAccessor):
    __types = (pd.DataFrame, pd.Series)

    __INDEX_COL = "_tp_index"

    __AGGREGATE_FUNCTIONS: t.List[str] = ["count", "sum", "mean", "median", "min", "max", "std", "first", "last"]

    def to_pandas(self, value: t.Union[pd.DataFrame, pd.Series]) -> t.Union[t.List[pd.DataFrame], pd.DataFrame]:
        return self.__to_dataframe(value)

    def __to_dataframe(self, value: t.Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
        if isinstance(value, pd.Series):
            return pd.DataFrame(value)
        return t.cast(pd.DataFrame, value)

    def _from_pandas(self, value: pd.DataFrame, data_type: t.Type) -> t.Any:
        if data_type is pd.Series:
            return value.iloc[:, 0]
        return value

    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return list(_PandasDataAccessor.__types)

    @staticmethod
    def __user_function(
        row: pd.Series, gui: Gui, column_name: t.Optional[str], user_function: t.Callable, function_name: str
    ) -> str:  # pragma: no cover
        args = []
        if column_name:
            args.append(row[column_name])
        args.extend((row.name, row))  # type: ignore[arg-type]
        if column_name:
            args.append(column_name)  # type: ignore[arg-type]
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
        payload_cols: t.Any,
        dataframe: pd.DataFrame,
        styles: t.Optional[t.Dict[str, str]] = None,
        tooltips: t.Optional[t.Dict[str, str]] = None,
        is_copied: t.Optional[bool] = False,
        new_indexes: t.Optional[np.ndarray] = None,
        handle_nan: t.Optional[bool] = False,
        formats: t.Optional[t.Dict[str, str]] = None,
    ) -> pd.DataFrame:
        dataframe = dataframe.iloc[new_indexes] if new_indexes is not None else dataframe
        if isinstance(payload_cols, list) and len(payload_cols):
            col_types = dataframe.dtypes[dataframe.dtypes.index.astype(str).isin(payload_cols)]
        else:
            col_types = dataframe.dtypes
        cols = col_types.index.astype(str).tolist()
        new_cols = {}
        if styles:
            for k, v in styles.items():
                col_applied = ""
                new_data = None
                func = self._gui._get_user_function(v)
                if callable(func):
                    col_applied, new_data = self.__apply_user_function(
                        func, k if k in cols else None, v, dataframe, "tps__"
                    )
                new_cols[col_applied or v] = new_data if col_applied else v
        if tooltips:
            for k, v in tooltips.items():
                func = self._gui._get_user_function(v)
                if callable(func):
                    col_applied, new_data = self.__apply_user_function(
                        func, k if k in cols else None, v, dataframe, "tpt__"
                    )
                    if col_applied:
                        new_cols[col_applied] = new_data
        if formats:
            for k, v in formats.items():
                func = self._gui._get_user_function(v)
                if callable(func):
                    col_applied, new_data = self.__apply_user_function(
                        func, k if k in cols else None, v, dataframe, "tpf__"
                    )
                    if col_applied:
                        new_cols[col_applied] = new_data
        # deal with dates
        date_cols = col_types[col_types.astype(str).str.startswith("datetime")].index.tolist()
        if len(date_cols) != 0:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                dataframe = dataframe.copy()
            tz = Gui._get_timezone()
            for col in date_cols:
                new_col = _get_date_col_str_name(cols, col)
                re_type = _RE_PD_TYPE.match(str(col_types[col]))
                groups = re_type.groups() if re_type else ()
                if len(groups) > 4 and groups[4]:
                    new_cols[new_col] = (
                        dataframe[col]
                        .dt.tz_convert("UTC")
                        .dt.strftime(_DataAccessor._WS_DATE_FORMAT)
                        .astype(str)
                        .replace("nan", "NaT" if handle_nan else None)
                    )
                else:
                    new_cols[new_col] = (
                        dataframe[col]
                        .dt.tz_localize(tz)
                        .dt.tz_convert("UTC")
                        .dt.strftime(_DataAccessor._WS_DATE_FORMAT)
                        .astype(str)
                        .replace("nan", "NaT" if handle_nan else None)
                    )

            # remove the date columns from the list of columns
            cols = list(set(cols) - set(date_cols))
        if new_cols:
            dataframe = dataframe.assign(**new_cols)
        cols += list(new_cols.keys())
        dataframe = dataframe.loc[:, dataframe.dtypes[dataframe.dtypes.index.astype(str).isin(cols)].index]  # type: ignore[index]
        return dataframe

    def __apply_user_function(
        self,
        user_function: t.Callable,
        column_name: t.Optional[str],
        function_name: str,
        data: pd.DataFrame,
        prefix: t.Optional[str],
    ):
        try:
            new_col_name = f"{prefix}{column_name}__{function_name}" if column_name else function_name
            return new_col_name, data.apply(
                _PandasDataAccessor.__user_function,
                axis=1,
                args=(self._gui, column_name, user_function, function_name),
            )
        except Exception as e:
            _warn(f"Exception raised when invoking user function {function_name}()", e)
        return "", data

    def __format_data(
        self,
        data: pd.DataFrame,
        data_format: _DataFormat,
        orient: str,
        start: t.Optional[int] = None,
        rowcount: t.Optional[int] = None,
        data_extraction: t.Optional[bool] = None,
        handle_nan: t.Optional[bool] = False,
        fullrowcount: t.Optional[int] = None,
    ) -> t.Dict[str, t.Any]:
        ret: t.Dict[str, t.Any] = {
            "format": str(data_format.value),
        }
        if rowcount is not None:
            ret["rowcount"] = rowcount
        if fullrowcount is not None and fullrowcount != rowcount:
            ret["fullrowcount"] = fullrowcount
        if start is not None:
            ret["start"] = start
        if data_extraction is not None:
            ret["dataExtraction"] = data_extraction  # Extract data out of dictionary on front-end
        if data_format is _DataFormat.APACHE_ARROW:
            if not _has_arrow_module:
                raise RuntimeError("Cannot use Arrow as pyarrow package is not installed")
            # Convert from pandas to Arrow
            table = pa.Table.from_pandas(data)  # type: ignore[reportPossiblyUnboundVariable]
            # Create sink buffer stream
            sink = pa.BufferOutputStream()  # type: ignore[reportPossiblyUnboundVariable]
            # Create Stream writer
            writer = pa.ipc.new_stream(sink, table.schema)  # type: ignore[reportPossiblyUnboundVariable]
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
        if isinstance(value, list):
            ret_dict: t.Dict[str, str] = {}
            for i, v in enumerate(value):
                ret_dict.update(
                    {f"{i}/{k}": v for k, v in self.__to_dataframe(v).dtypes.apply(lambda x: x.name.lower()).items()}
                )
            return ret_dict
        return {str(k): v for k, v in self.__to_dataframe(value).dtypes.apply(lambda x: x.name.lower()).items()}

    def __get_data(  # noqa: C901
        self,
        var_name: str,
        df: pd.DataFrame,
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

        orig_df = df
        # add index if not chart
        if paged:
            if _PandasDataAccessor.__INDEX_COL not in df.columns:
                is_copied = True
                df = df.assign(**{_PandasDataAccessor.__INDEX_COL: df.index})
            if columns and _PandasDataAccessor.__INDEX_COL not in columns:
                columns.append(_PandasDataAccessor.__INDEX_COL)

        fullrowcount = len(df)
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
                    if self.__is_date_column(t.cast(pd.DataFrame, df), col):
                        val = datetime.fromisoformat(val[:-1])
                    vars.append(val)
                val = f"@vars[{len(vars) - 1}]" if isinstance(val, (str, datetime)) else val
                right = f".str.contains({val})" if action == "contains" else f" {action} {val}"
                if query:
                    query += " and "
                query += f"`{col}`{right}"
            try:
                df = df.query(query)
                is_copied = True
            except Exception as e:
                _warn(f"Dataframe filtering: invalid query '{query}' on {df.head()}", e)

        dict_ret: t.Optional[t.Dict[str, t.Any]]
        if paged:
            aggregates = payload.get("aggregates")
            applies = payload.get("applies")
            if isinstance(aggregates, list) and len(aggregates) and isinstance(applies, dict):
                applies_with_fn = {
                    k: v if v in _PandasDataAccessor.__AGGREGATE_FUNCTIONS else self._gui._get_user_function(v)
                    for k, v in applies.items()
                }

                for col in columns:
                    if col not in applies_with_fn.keys():
                        applies_with_fn[col] = "first"
                try:
                    df = t.cast(pd.DataFrame, df).groupby(aggregates).agg(applies_with_fn)
                except Exception:
                    _warn(f"Cannot aggregate {var_name} with groupby {aggregates} and aggregates {applies}.")
            inf = payload.get("infinite")
            if inf is not None:
                ret_payload["infinite"] = inf
            # real number of rows is needed to calculate the number of pages
            rowcount = len(df)
            # here we'll deal with start and end values from payload if present
            if isinstance(payload.get("start", 0), int):
                start = int(payload.get("start", 0))
            else:
                try:
                    start = int(str(payload["start"]), base=10)
                except Exception:
                    _warn(f'start should be an int value {payload["start"]}.')
                    start = 0
            if isinstance(payload.get("end", -1), int):
                end = int(payload.get("end", -1))
            else:
                try:
                    end = int(str(payload["end"]), base=10)
                except Exception:
                    end = -1
            if start < 0 or start >= rowcount:
                start = 0
            if end < 0 or end >= rowcount:
                end = rowcount - 1
            if payload.get("reverse", False):
                diff = end - start
                end = rowcount - 1 - start
                if end < 0:
                    end = rowcount - 1
                start = end - diff
                if start < 0:
                    start = 0
            # deal with sort
            order_by = payload.get("orderby")
            if isinstance(order_by, str) and len(order_by):
                try:
                    if df.columns.dtype.name == "int64":
                        order_by = int(order_by)
                    new_indexes = t.cast(pd.DataFrame, df)[order_by].values.argsort(axis=0)
                    if payload.get("sort") == "desc":
                        # reverse order
                        new_indexes = new_indexes[::-1]
                    new_indexes = new_indexes[slice(start, end + 1)]
                except Exception:
                    _warn(f"Cannot sort {var_name} on columns {order_by}.")
                    new_indexes = slice(start, end + 1)  # type: ignore
            else:
                new_indexes = slice(start, end + 1)  # type: ignore
            df = self.__build_transferred_cols(
                columns,
                t.cast(pd.DataFrame, df),
                styles=payload.get("styles"),
                tooltips=payload.get("tooltips"),
                is_copied=is_copied,
                new_indexes=t.cast(np.ndarray, new_indexes),
                handle_nan=payload.get("handlenan", False),
                formats=payload.get("formats"),
            )
            dict_ret = self.__format_data(
                df,
                data_format,
                "records",
                start,
                rowcount,
                handle_nan=payload.get("handlenan", False),
                fullrowcount=fullrowcount,
            )
            compare = payload.get("compare")
            if isinstance(compare, str):
                comp_df = _compare_function(
                    self._gui, compare, var_name, t.cast(pd.DataFrame, orig_df), payload.get("compare_datas", "")
                )
                if isinstance(comp_df, pd.DataFrame) and not comp_df.empty:
                    try:
                        if isinstance(comp_df.columns[0], tuple):
                            cols: t.List[t.Hashable] = [c for c in comp_df.columns if c[1] == "other"]
                            comp_df = t.cast(pd.DataFrame, comp_df.get(cols))
                            comp_df.columns = t.cast(pd.Index, [t.cast(tuple, c)[0] for c in cols])
                        comp_df.dropna(axis=1, how="all", inplace=True)
                        comp_df = self.__build_transferred_cols(
                            columns, comp_df, new_indexes=t.cast(np.ndarray, new_indexes)
                        )
                        dict_ret["comp"] = self.__format_data(comp_df, data_format, "records").get("data")
                    except Exception as e:
                        _warn("Pandas accessor compare raised an exception", e)

        else:
            ret_payload["alldata"] = True
            decimator_payload: t.Dict[str, t.Any] = payload.get("decimatorPayload", {})
            decimators = decimator_payload.get("decimators", [])
            nb_rows_max = decimator_payload.get("width")
            for decimator_pl in decimators:
                decimator = decimator_pl.get("decimator")
                decimator_instance = (
                    self._gui._get_user_instance(decimator, PropertyType.decimator.value)
                    if decimator is not None
                    else None
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

                        df, is_copied = _df_relayout(
                            t.cast(pd.DataFrame, df), x_column, y_column, chart_mode, x0, x1, y0, y1, is_copied
                        )

                    if nb_rows_max and decimator_instance._is_applicable(df, nb_rows_max, chart_mode):
                        try:
                            df, is_copied = _df_data_filter(
                                t.cast(pd.DataFrame, df),
                                x_column,
                                y_column,
                                z_column,
                                decimator=decimator_instance,
                                payload=decimator_payload,
                                is_copied=is_copied,
                            )
                            self._gui._call_on_change(f"{var_name}.{decimator}.nb_rows", len(df))
                        except Exception as e:
                            _warn(f"Limit rows error with {decimator} for Dataframe", e)
            if data_format is _DataFormat.CSV:
                df = self.__build_transferred_cols(
                    columns,
                    t.cast(pd.DataFrame, df),
                    is_copied=is_copied,
                    handle_nan=payload.get("handlenan", False),
                )
                ret_payload["df"] = df
                dict_ret = None
            else:
                df = self.__build_transferred_cols(
                    columns,
                    t.cast(pd.DataFrame, df),
                    styles=payload.get("styles"),
                    tooltips=payload.get("tooltips"),
                    is_copied=is_copied,
                    handle_nan=payload.get("handlenan", False),
                    formats=payload.get("formats"),
                )
                dict_ret = self.__format_data(df, data_format, "list", data_extraction=True)

        ret_payload["value"] = dict_ret
        return ret_payload

    def get_data(
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
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
                        self.__get_data(var_name, self.__to_dataframe(v), payload, data_format, f"{i}/")
                        if isinstance(v, _PandasDataAccessor.__types)
                        else {}
                    )
                    ret_val = ret.get("value", {})
                    data.append(ret_val.pop("data", None))
                    ret_payload.get("value", {}).update(ret_val)
                ret_payload["value"]["data"] = data
                return ret_payload
            else:
                value = value[0]
        return self.__get_data(var_name, self.__to_dataframe(value), payload, data_format)

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Cannot edit {type(value)}.")
        df.at[payload["index"], payload["col"]] = payload["value"]
        return self._from_pandas(df, type(value))

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Cannot delete a row from {type(value)}.")
        return self._from_pandas(df.drop(payload["index"]), type(value))

    def on_add(self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Cannot add a row to {type(value)}.")
        # Save the insertion index
        index = payload["index"]
        # Create the new row (Column value types must match the original DataFrame's)
        col_types = self.get_col_types("", df)
        if col_types:
            new_row = [0 if is_numeric_dtype(df[c]) else "" for c in list(col_types)] if new_row is None else new_row
            if index > 0:
                # Column names and value types must match the original DataFrame
                new_df = pd.DataFrame([new_row], columns=list(col_types))
                # Split the DataFrame
                rows_before = df.iloc[:index]
                rows_after = df.iloc[index:]
                return self._from_pandas(pd.concat([rows_before, new_df, rows_after], ignore_index=True), type(value))
            else:
                df = df.copy()
                # Insert as the new first row
                df.loc[-1] = new_row  # Insert the new row
                df.index = df.index + 1  # Shift index
                return self._from_pandas(df.sort_index(), type(value))
        return value

    def to_csv(self, var_name: str, value: t.Any):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Cannot export {type(value)} to csv.")
        dict_ret = self.__get_data(var_name, df, {"alldata": True}, _DataFormat.CSV)
        if isinstance(dict_ret, dict):
            dfr = dict_ret.get("df")
            if isinstance(dfr, pd.DataFrame):
                fd, temp_path = mkstemp(".csv", var_name, text=True)
                with os.fdopen(fd, "wt", newline="") as csv_file:
                    dfr.to_csv(csv_file, index=False)

                return temp_path
        return None
