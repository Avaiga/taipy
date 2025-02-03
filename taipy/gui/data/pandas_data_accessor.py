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

_has_arrow_module = False
if util.find_spec("pyarrow"):
    _has_arrow_module = True
    import pyarrow as pa

_ORIENT_TYPE = t.Literal["records", "list"]


class _PandasDataAccessor(_DataAccessor):
    __types = (pd.DataFrame, pd.Series)

    __INDEX_COL = "_tp_index"

    __AGGREGATE_FUNCTIONS: t.List[str] = ["count", "sum", "mean", "median", "min", "max", "std", "first", "last"]

    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return list(_PandasDataAccessor.__types)

    def to_pandas(self, value: t.Union[pd.DataFrame, pd.Series]) -> t.Union[t.List[pd.DataFrame], pd.DataFrame]:
        return self._to_dataframe(value)

    def _to_dataframe(self, value: t.Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
        if isinstance(value, pd.Series):
            return pd.DataFrame(value)
        return t.cast(pd.DataFrame, value)

    def _from_pandas(self, value: pd.DataFrame, data_type: t.Type) -> t.Any:
        if data_type is pd.Series:
            return value.iloc[:, 0]
        return value

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

    def __get_column_names(self, df: pd.DataFrame, *cols: str):
        col_names = [t for t in df.columns if str(t) in cols]
        return (col_names[0] if len(cols) == 1 else col_names) if col_names else None

    def get_dataframe_with_cols(self, df: pd.DataFrame, cols: t.List[str]) -> pd.DataFrame:
        return df.loc[:, df.dtypes[df.columns.astype(str).isin(cols)].index]  # type: ignore[index]

    def __build_transferred_cols(  # noqa: C901
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
            cols_description = {k: v for k, v in self.get_cols_description("", dataframe).items() if k in payload_cols}
        else:
            cols_description = self.get_cols_description("", dataframe)
        cols = list(cols_description.keys())
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
        date_cols = [c for c, d in cols_description.items() if d.get("type", "").startswith("datetime")]
        if len(date_cols) != 0:
            if not is_copied:
                # copy the df so that we don't "mess" with the user's data
                dataframe = dataframe.copy()
            tz = Gui._get_timezone()
            for col in date_cols:
                col_name = self.__get_column_names(dataframe, col)
                new_col = _get_date_col_str_name(cols, col)
                re_type = _RE_PD_TYPE.match(cols_description[col].get("type", ""))
                groups = re_type.groups() if re_type else ()
                if len(groups) > 4 and groups[4]:
                    new_cols[new_col] = (
                        dataframe[col_name]
                        .dt.tz_convert("UTC")
                        .dt.strftime(_DataAccessor._WS_DATE_FORMAT)
                        .astype(str)
                        .replace("nan", "NaT" if handle_nan else None)
                    )
                else:
                    new_cols[new_col] = (
                        dataframe[col_name]
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
        return self.get_dataframe_with_cols(dataframe, cols)

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
                args=(
                    self._gui,
                    self.__get_column_names(data, column_name) if column_name else column_name,
                    user_function,
                    function_name,
                ),
            )
        except Exception as e:
            _warn(f"Exception raised when invoking user function {function_name}()", e)
        return "", data

    def _format_data(
        self,
        data: pd.DataFrame,
        data_format: _DataFormat,
        orient: _ORIENT_TYPE,
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
            ret["data"] = self.get_json_ready_dict(data.replace([np.nan, pd.NA], [None, None]), orient)
        return ret

    def get_json_ready_dict(self, df: pd.DataFrame, orient: _ORIENT_TYPE) -> t.Dict[t.Hashable, t.Any]:
        return df.to_dict(orient=orient)  # type: ignore[return-value]

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Dict[str, t.Dict[str, str]]:
        if isinstance(value, list):
            ret_dict: t.Dict[str, t.Dict[str, str]] = {}
            for i, v in enumerate(value):
                res = self.get_cols_description("", v)
                if res:
                    ret_dict.update({f"{i}/{k}": desc for k, desc in res.items()})
            return ret_dict
        df = self._to_dataframe(value)
        return {str(k): {"type": v} for k, v in df.dtypes.apply(lambda x: x.name.lower()).items()}

    def add_optional_columns(self, df: pd.DataFrame, columns: t.List[str]) -> t.Tuple[pd.DataFrame, t.List[str]]:
        return df, []

    def is_dataframe_supported(self, df: pd.DataFrame) -> bool:
        return not isinstance(df.columns, pd.MultiIndex)

    def __get_data(  # noqa: C901
        self,
        var_name: str,
        df: pd.DataFrame,
        payload: t.Dict[str, t.Any],
        data_format: _DataFormat,
        col_prefix: t.Optional[str] = "",
    ) -> t.Dict[str, t.Any]:
        ret_payload = {"pagekey": payload.get("pagekey", "unknown page")}
        if not self.is_dataframe_supported(df):
            ret_payload["value"] = {}
            ret_payload["error"] = "MultiIndex columns are not supported."
            _warn("MultiIndex columns are not supported.")
            return ret_payload
        columns = payload.get("columns", [])
        if col_prefix:
            columns = [c[len(col_prefix) :] if c.startswith(col_prefix) else c for c in columns]
        paged = not payload.get("alldata", False)
        is_copied = False

        orig_df = df
        # add index if not chart
        if paged:
            if _PandasDataAccessor.__INDEX_COL not in df.columns:
                is_copied = True
                df = df.assign(**{_PandasDataAccessor.__INDEX_COL: df.index.to_numpy()})
            if columns and _PandasDataAccessor.__INDEX_COL not in columns:
                columns.append(_PandasDataAccessor.__INDEX_COL)
        # optional columns
        df, optional_columns = self.add_optional_columns(df, columns)
        is_copied = is_copied or bool(optional_columns)

        fullrowcount = len(df)
        # filtering
        filters = payload.get("filters")
        if isinstance(filters, list) and len(filters) > 0:
            query = ""
            vars = []
            cols_description = self.get_cols_description(var_name, df)
            for fd in filters:
                col = fd.get("col")
                val = fd.get("value")
                action = fd.get("action")
                match_case = fd.get("matchCase", False) is not False  # Ensure it's a boolean
                right = None
                col_expr = f"`{col}`"

                if isinstance(val, str):
                    if cols_description.get(col, {}).get("type", "").startswith("datetime"):
                        val = datetime.fromisoformat(val[:-1])
                    elif not match_case:
                        if action != "contains":
                            col_expr = f"{col_expr}.str.lower()"
                        val = val.lower()
                    vars.append(val)
                    val_var = f"@vars[{len(vars) - 1}]"
                    if action == "contains":
                        right = f".str.contains({val_var}{'' if match_case else ', case=False'})"
                else:
                    vars.append(val)
                    val_var = f"@vars[{len(vars) - 1}]"

                if right is None:
                    right = f" {action} {val_var}"

                if query:
                    query += " and "
                query += f"{col_expr}{right}"

            # Apply filters using df.query()
            try:
                if query:
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
                    self.__get_column_names(df, k): v
                    if v in _PandasDataAccessor.__AGGREGATE_FUNCTIONS
                    else self._gui._get_user_function(v)
                    for k, v in applies.items()
                }

                for col in df.columns:
                    if col not in applies_with_fn:
                        applies_with_fn[col] = "first"
                try:
                    col_names = self.__get_column_names(df, *aggregates)
                    if col_names:
                        df = t.cast(pd.DataFrame, df).groupby(aggregates).agg(applies_with_fn)
                    else:
                        raise Exception()
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
                    col_name = self.__get_column_names(df, order_by)
                    if col_name:
                        new_indexes = t.cast(pd.DataFrame, df)[col_name].values.argsort(axis=0)
                        if payload.get("sort") == "desc":
                            # reverse order
                            new_indexes = new_indexes[::-1]
                        new_indexes = new_indexes[slice(start, end + 1)]
                    else:
                        raise Exception()
                except Exception:
                    _warn(f"Cannot sort {var_name} on columns {order_by}.")
                    new_indexes = slice(start, end + 1)  # type: ignore
            else:
                new_indexes = slice(start, end + 1)  # type: ignore
            df = self.__build_transferred_cols(
                columns + optional_columns,
                t.cast(pd.DataFrame, df),
                styles=payload.get("styles"),
                tooltips=payload.get("tooltips"),
                is_copied=is_copied,
                new_indexes=t.cast(np.ndarray, new_indexes),
                handle_nan=payload.get("handlenan", False),
                formats=payload.get("formats"),
            )
            dict_ret = self._format_data(
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
                        dict_ret["comp"] = self._format_data(comp_df, data_format, "records").get("data")
                    except Exception as e:
                        _warn("Pandas accessor compare raised an exception", e)

        else:
            ret_payload["alldata"] = True
            decimator_payload: t.Dict[str, t.Any] = payload.get("decimatorPayload", {})
            decimators = decimator_payload.get("decimators", [])
            decimated_dfs: t.List[pd.DataFrame] = []
            for decimator_pl in decimators:
                if decimator_pl is None:
                    continue
                decimator = decimator_pl.get("decimator")
                if decimator is None:
                    x_column = decimator_pl.get("xAxis", "")
                    y_column = decimator_pl.get("yAxis", "")
                    z_column = decimator_pl.get("zAxis", "")
                    filtered_columns = [x_column, y_column, z_column] if z_column else [x_column, y_column]
                    decimated_df = df.copy().filter(filtered_columns, axis=1)
                    decimated_dfs.append(decimated_df)
                    continue
                decimator_instance = (
                    self._gui._get_user_instance(decimator, PropertyType.decimator.value)
                    if decimator is not None
                    else None
                )
                if isinstance(decimator_instance, PropertyType.decimator.value):
                    # Run the on_decimate method -> check if the decimator should be applied
                    # -> apply the decimator
                    decimated_df, is_decimator_applied, is_copied = decimator_instance._on_decimate(
                        df, decimator_pl, decimator_payload, is_copied
                    )
                    # add decimated dataframe to the list of decimated
                    decimated_dfs.append(decimated_df)
                    if is_decimator_applied:
                        self._gui._call_on_change(f"{var_name}.{decimator}.nb_rows", len(decimated_df))
            # merge the decimated dataFrames
            if len(decimated_dfs) > 1:
                # get the unique columns from all decimated dataFrames
                decimated_columns = pd.Index([])
                for _df in decimated_dfs:
                    decimated_columns = decimated_columns.append(_df.columns)
                # find the columns that are duplicated across dataFrames
                overlapping_columns = decimated_columns[decimated_columns.duplicated()].unique()
                # concatenate the dataFrames without overwriting columns
                merged_df = pd.concat(decimated_dfs, axis=1)
                # resolve overlapping columns by combining values
                for col in overlapping_columns:
                    # for each overlapping column, combine the values across dataFrames
                    # (e.g., take the first non-null value)
                    cols_to_combine = merged_df.loc[:, col].columns
                    merged_df[col] = merged_df[cols_to_combine].bfill(axis=1).iloc[:, 0]
                # drop duplicated col since they are now the same
                df = merged_df.loc[:, ~merged_df.columns.duplicated()]
            elif len(decimated_dfs) == 1:
                df = decimated_dfs[0]
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
                dict_ret = self._format_data(df, data_format, "list", data_extraction=True)

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
                        self.__get_data(var_name, self._to_dataframe(v), payload, data_format, f"{i}/")
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
        return self.__get_data(var_name, self._to_dataframe(value), payload, data_format)

    def _get_index_value(self, index: t.Any) -> t.Any:
        return tuple(index) if isinstance(index, list) else index

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame) or not isinstance(payload.get("index"), (int, float)):
            raise ValueError(f"Cannot edit {type(value)} at {payload.get('index')}.")
        df.at[self._get_index_value(payload.get("index", 0)), payload["col"]] = payload["value"]
        return self._from_pandas(df, type(value))

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame) or not isinstance(payload.get("index"), (int, float)):
            raise ValueError(f"Cannot delete a row from {type(value)} at {payload.get('index')}.")
        return self._from_pandas(df.drop(self._get_index_value(payload.get("index", 0))), type(value))

    def on_add(self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None):
        df = self.to_pandas(value)
        if not isinstance(df, pd.DataFrame) or not isinstance(payload.get("index"), (int, float)):
            raise ValueError(f"Cannot add a row to {type(value)} at {payload.get('index')}.")
        # Save the insertion index
        index = payload.get("index", 0)
        # Create the new row (Column value types must match the original DataFrame's)
        if list(df.columns):
            new_row = [0 if is_numeric_dtype(dt) else "" for dt in df.dtypes] if new_row is None else new_row
            if index > 0:
                # Column names and value types must match the original DataFrame
                new_df = pd.DataFrame([new_row], columns=df.columns.copy())
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
