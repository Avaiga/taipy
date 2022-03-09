import typing as t

import numpy
import pandas as pd

from ..gui import Gui
from .data_format import _DataFormat
from .pandas_data_accessor import _PandasDataAccessor


class _NumpyDataAccessor(_PandasDataAccessor):

    __types = (numpy.ndarray,)

    @staticmethod
    def get_supported_classes() -> t.List[str]:
        return [t.__name__ for t in _NumpyDataAccessor.__types]

    def __get_dataframe(self, value: t.Any) -> pd.DataFrame:
        return pd.DataFrame(value)

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        if isinstance(value, _NumpyDataAccessor.__types):
            return super().get_col_types(var_name, self.__get_dataframe(value))
        return None

    def get_data(  # noqa: C901
        self, guiApp: Gui, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        if isinstance(value, _NumpyDataAccessor.__types):
            return super().get_data(guiApp, var_name, self.__get_dataframe(value), payload, data_format)
        return {}
