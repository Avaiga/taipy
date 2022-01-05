from types import FunctionType
import typing as t
import warnings

import pandas as pd
import pyarrow as pa
from pandas.core.frame import DataFrame

from ..utils import _get_date_col_str_name, _get_dict_value
from .data_accessor import DataAccessor
from .data_format import DataFormat

if t.TYPE_CHECKING:
    from ..gui import Gui


class PandasDataAccessor(DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.Callable:  # type: ignore
        return pd.DataFrame

    def __build_transferred_cols(
        self, guiApp: t.Any, payload_cols: t.Any, data: pd.DataFrame, styles: t.Optional[t.Dict[str, str]] = None
    ) -> pd.DataFrame:
        if isinstance(payload_cols, list) and len(payload_cols):
            col_types = data.dtypes[data.dtypes.index.isin(payload_cols)]
        else:
            col_types = data.dtypes
        cols = col_types.index.tolist()
        is_copied = False
        # deal with dates
        datecols = col_types[col_types.astype("string").str.startswith("datetime")].index.tolist()
        if len(datecols) != 0:
            # copy the df so that we don't "mess" with the user's data
            data = data.copy()
            is_copied = True
            for col in datecols:
                newcol = _get_date_col_str_name(cols, col)
                cols.append(newcol)
                data[newcol] = data[col].dt.strftime(DataAccessor._WS_DATE_FORMAT).astype("string")
            # remove the date columns from the list of columns
            cols = list(set(cols) - set(datecols))
        data = data.loc[:, cols]
        if styles:
            if not is_copied:
                data = data.copy()
            for k, v in styles.items():
                applied = False
                if hasattr(guiApp, v):
                    style_fn = getattr(guiApp, v)
                    if isinstance(style_fn, FunctionType):
                        applied = self.__apply_user_function(style_fn, k, v, data)
                if not applied:
                    data[v] = v
        return data

    def __apply_user_function(
        self, user_function: FunctionType, column_name: str, function_name: str, data: pd.DataFrame
    ):
        arg_count = user_function.__code__.co_argcount
        args = []
        if arg_count > 0 and arg_count < 3:
            if arg_count > 1:
                args.append(column_name)
            data[function_name] = data.apply(user_function, axis=1, args=tuple(args))
            return True
        else:
            warnings.warn(f"Style function {function_name} should take at least a series (row) as first argument")
        return False

    def __format_data(
        self,
        data: DataFrame,
        data_format: DataFormat,
        orient: str = None,
        start: t.Optional[int] = None,
        rowcount: t.Optional[int] = None,
        data_extraction: t.Optional[bool] = None,
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
        if data_format == DataFormat.APACHE_ARROW:
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
        else:
            ret["data"] = data.to_dict(orient=orient)
        return ret

    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        if isinstance(value, pd.DataFrame):
            warnings.warn("Error: cannot update value for dataframe: " + var_name)
            return None
        return value

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, pd.DataFrame):
            return value.dtypes.apply(lambda x: x.name).to_dict()
        return None

    def get_data(  # noqa: C901
        self, guiApp: t.Any, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
        ret_payload = {}
        if isinstance(value, pd.DataFrame):
            aggregates = _get_dict_value(payload, "aggregates")
            applies = _get_dict_value(payload, "applies")
            if isinstance(aggregates, list) and len(aggregates) and isinstance(applies, dict):
                applies_with_fn = {}
                for k, v in applies.items():
                    applies_with_fn[k] = getattr(guiApp, v) if hasattr(guiApp, v) else v
                for col in _get_dict_value(payload, "columns") or []:
                    if col not in applies_with_fn.keys():
                        applies_with_fn[col] = "first"
                try:
                    value = value.groupby(aggregates).agg(applies_with_fn)
                except Exception:
                    warnings.warn(f"Cannot aggregate {var_name} with groupby {aggregates} and aggregates {applies}")
            paged = not _get_dict_value(payload, "alldata")
            if paged:
                keys = payload.keys()
                ret_payload["pagekey"] = payload["pagekey"] if "pagekey" in keys else "unknown page"
                if "infinite" in keys:
                    ret_payload["infinite"] = payload["infinite"]
            else:
                ret_payload["alldata"] = payload["alldata"]
                nb_rows_max = _get_dict_value(payload, "width")
            columns = _get_dict_value(payload, "columns")
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
                value = self.__build_transferred_cols(
                    guiApp, columns, value.iloc[new_indexes], styles=_get_dict_value(payload, "styles")
                )
                dictret = self.__format_data(value, data_format, "records", start, rowcount)
            else:
                # view with the requested columns
                if nb_rows_max and nb_rows_max < len(value) / 2:
                    value = value.copy()
                    value["tp_index"] = value.index
                    # we need to be more clever than this :-)
                    value = value.iloc[:: (len(value) // nb_rows_max)]
                value = self.__build_transferred_cols(guiApp, columns, value)
                dictret = self.__format_data(value, data_format, "list", data_extraction=True)
            ret_payload["value"] = dictret
        return ret_payload

    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return isinstance(value, pd.DataFrame)
