import typing as t

import pandas as pd

from .data_format import DataFormat
from .pandas_data_accessor import PandasDataAccessor
from ..gui import Gui


class ArrayDictDataAccessor(PandasDataAccessor):

    __types = (dict, list, tuple)

    @staticmethod
    def get_supported_classes() -> t.List[str]:
        return [t.__name__ for t in ArrayDictDataAccessor.__types]

    def __get_dataframe(self, value: t.Any) -> pd.DataFrame:
        if isinstance(value, (list)):
            if isinstance(value[0], (str, int, float, bool)):
                return pd.DataFrame({"0": value})
            elif isinstance(value[0], list):
                return pd.DataFrame({str(i): v for i, v in enumerate(value)})
        return pd.DataFrame(value)

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, ArrayDictDataAccessor.__types):
            return super().get_col_types(var_name, self.__get_dataframe(value))
        return None

    def get_data(  # noqa: C901
        self, guiApp: Gui, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: DataFormat
    ) -> t.Dict[str, t.Any]:
        if isinstance(value, ArrayDictDataAccessor.__types):
            return super().get_data(guiApp, var_name, self.__get_dataframe(value), payload, data_format)
        return {}
