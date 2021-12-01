import typing as t
import warnings

import pandas as pd
import pyarrow as pa
from pandas.core.frame import DataFrame

from ..utils import _get_date_col_str_name, _get_dict_value
from .data_accessor import DataAccessor
from .data_format import DataFormat


class PandasDataAccessor(DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.Callable:  # type: ignore
        return pd.DataFrame

    def _format_data(self, data: DataFrame, data_format: DataFormat, orient: str = None) -> t.Union[t.Dict, bytes]:
        if data_format == DataFormat.JSON:
            return data.to_dict(orient=orient)
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
            return buf.to_pybytes()

    def cast_string_value(self, var_name: str, value: t.Any) -> t.Any:
        if isinstance(value, pd.DataFrame):
            warnings.warn("Error: cannot update value for dataframe: " + var_name)
            return None
        return value

    def is_data_access(self, var_name: str, value: t.Any) -> bool:
        return isinstance(value, pd.DataFrame)

    def get_data(  # noqa: C901
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
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
                nb_rows_max = _get_dict_value(payload, "width")
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
                dictret = {
                    "data": self._format_data(value, data_format, "records"),
                    "orient": "records",
                    "rowcount": rowcount,
                    "start": start,
                    "format": str(data_format.value),
                }
            else:
                # view with the requested columns
                if nb_rows_max and nb_rows_max < len(value) / 2:
                    value = value.loc[:, cols]
                    value["tp_index"] = value.index
                    # we need to be more clever than this :-)
                    value = value.iloc[:: (len(value) // nb_rows_max)]
                else:
                    value = value.loc[:, cols]
                dictret = {
                    "data": self._format_data(value, data_format, "list"),
                    "orient": "list",
                    "format": str(data_format.value),
                    "dataExtraction": True,  # Extract data out of dictionary on frontend
                }
            ret_payload["value"] = dictret
        return ret_payload

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, pd.DataFrame):
            return value.dtypes.apply(lambda x: x.name).to_dict()
        return None
