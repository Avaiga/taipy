import typing as t

import pandas as pd

from ..gui import Gui
from .data_format import _DataFormat
from .pandas_data_accessor import _PandasDataAccessor


class _ArrayDictDataAccessor(_PandasDataAccessor):

    __types = (dict, list, tuple)

    @staticmethod
    def get_supported_classes() -> t.List[str]:
        return [t.__name__ for t in _ArrayDictDataAccessor.__types]  # type: ignore

    def __get_dataframe(self, value: t.Any) -> t.Union[t.List[pd.DataFrame], pd.DataFrame]:
        if isinstance(value, list):
            if isinstance(value[0], (str, int, float, bool)):
                return pd.DataFrame({"0": value})
            types = {type(x) for x in value}
            if len(types) == 1 and next(iter(types), None) == list:
                lengths = {len(x) for x in value}
                return (
                    pd.DataFrame({str(i): v for i, v in enumerate(value)})
                    if len(lengths) == 1
                    else [pd.DataFrame({f"{i}/0": v}) for i, v in enumerate(value)]
                )

            elif pd.DataFrame in types:
                if len(types) == 1:
                    return value
                elif len(types) == 2 and list in types:
                    return [
                        v if isinstance(v, pd.DataFrame) else pd.DataFrame({str(i): v}) for i, v in enumerate(value)
                    ]
        return pd.DataFrame(value)

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, _ArrayDictDataAccessor.__types):  # type: ignore
            return super().get_col_types(var_name, self.__get_dataframe(value))
        return None

    def get_data(  # noqa: C901
        self, guiApp: Gui, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        if isinstance(value, _ArrayDictDataAccessor.__types):  # type: ignore
            return super().get_data(guiApp, var_name, self.__get_dataframe(value), payload, data_format)
        return {}
