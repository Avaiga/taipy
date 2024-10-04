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

from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from ..._warnings import _warn


class Decimator(ABC):
    """Base class for decimating chart data.

    *Decimating* is the term used to name the process of reducing the number of
    data points displayed in charts while retaining the overall shape of the traces.
    `Decimator` is a base class that does decimation on data sets.

    Taipy GUI comes out-of-the-box with several implementation of this class for
    different use cases.
    """

    _CHART_MODES: t.List[str] = []

    def __init__(
        self,
        threshold: t.Optional[int],
        zoom: t.Optional[bool],
        on_decimate: t.Optional[t.Callable] = None,
        apply_decimator: t.Optional[t.Callable] = None,
    ) -> None:  # noqa: E501
        """Initialize a new `Decimator`.

        Arguments:
            threshold (Optional[int]): The minimum amount of data points before the
                decimator class is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
            on_decimate (Optional[Callable]): an user-defined function that is executed when the decimator
                is found during runtime. This function can be used to provide custom decimation logic.
            apply_decimator (Optional[Callable]): an user-defined function that is executed when the decimator
                is applied to modify the data.
        """
        super().__init__()
        self.threshold = threshold
        self._zoom = zoom if zoom is not None else True
        self.__user_defined_on_decimate = on_decimate
        self.__user_defined_apply_decimator = apply_decimator

    def _is_applicable(self, data: t.Any, nb_rows_max: int, chart_mode: str):
        if chart_mode not in self._CHART_MODES:
            _warn(
                f"Decimator '{type(self).__name__}' is not optimized for chart mode '{chart_mode}'. Consider using other chart mode such as '{f'{chr(39)}, {chr(39)}'.join(self._CHART_MODES)}.'"  # noqa: E501
            )
        if self.threshold is None:
            if nb_rows_max < len(data):
                return True
        elif self.threshold < len(data):
            return True
        return False

    def __get_indexed_df_col(self, df):
        index = 0
        while f"tAiPy_index_{index}" in df.columns:
            index += 1
        result = f"tAiPy_index_{index}"
        df[result] = df.index
        return result

    def _df_relayout(
        self,
        dataframe: pd.DataFrame,
        x_column: t.Optional[str],
        y_column: str,
        chart_mode: str,
        x0: t.Optional[float],
        x1: t.Optional[float],
        y0: t.Optional[float],
        y1: t.Optional[float],
        is_copied: bool,
    ):
        if chart_mode not in ["lines+markers", "lines", "markers"]:
            _warn(
                f"Decimator zoom feature is not applicable for '{chart_mode}' chart_mode. It is only applicable for 'lines+markers', 'lines', and 'markers' chart modes."  # noqa: E501
            )
            return dataframe, is_copied
        # if chart data is invalid
        if x0 is None and x1 is None and y0 is None and y1 is None:
            return dataframe, is_copied
        df = dataframe if is_copied else dataframe.copy()
        is_copied = True
        has_x_col = True

        if not x_column:
            x_column = self.__get_indexed_df_col(df)
            has_x_col = False

        df_filter_conditions = []
        # filter by x column by default
        if x0 is not None:
            df_filter_conditions.append(df[x_column] > x0)
        if x1 is not None:
            df_filter_conditions.append(df[x_column] < x1)
        # y column will be filtered only if chart_mode is not lines+markers (eg. markers)
        if chart_mode not in ["lines+markers", "lines"]:
            if y0 is not None:
                df_filter_conditions.append(df[y_column] > y0)
            if y1 is not None:
                df_filter_conditions.append(df[y_column] < y1)
        if df_filter_conditions:
            df = df.loc[np.bitwise_and.reduce(df_filter_conditions)]
        if not has_x_col:
            df.drop(x_column, axis=1, inplace=True)
        return df, is_copied

    def _df_apply_decimator(
        self,
        dataframe: pd.DataFrame,
        x_column_name: t.Optional[str],
        y_column_name: str,
        z_column_name: str,
        payload: t.Dict[str, t.Any],
        is_copied: bool,
    ):
        df = dataframe if is_copied else dataframe.copy()
        if not x_column_name:
            x_column_name = self.__get_indexed_df_col(df)
        column_list = [x_column_name, y_column_name, z_column_name] if z_column_name else [x_column_name, y_column_name]
        points = df[column_list].to_numpy()
        mask = self.decimate(points, payload)
        return df[mask], is_copied

    def _on_decimate_df(
        self,
        df: pd.DataFrame,
        decimator_instance_payload: t.Dict[str, t.Any],
        decimator_payload: t.Dict[str, t.Any],
        is_copied: bool = False,
        filter_unused_columns: bool = True,
    ):
        decimator_var_name = decimator_instance_payload.get("decimator")
        x_column, y_column, z_column = (
            decimator_instance_payload.get("xAxis", ""),
            decimator_instance_payload.get("yAxis", ""),
            decimator_instance_payload.get("zAxis", ""),
        )
        chart_mode = decimator_instance_payload.get("chartMode", "")
        if self._zoom and "relayoutData" in decimator_payload is not None and not z_column:
            relayout_data = decimator_payload.get("relayoutData", {})
            x0 = relayout_data.get("xaxis.range[0]")
            x1 = relayout_data.get("xaxis.range[1]")
            y0 = relayout_data.get("yaxis.range[0]")
            y1 = relayout_data.get("yaxis.range[1]")

            df, is_copied = self._df_relayout(
                t.cast(pd.DataFrame, df), x_column, y_column, chart_mode, x0, x1, y0, y1, is_copied
            )

        nb_rows_max = decimator_payload.get("width")
        is_decimator_applied = False
        if nb_rows_max and self._is_applicable(df, nb_rows_max, chart_mode):
            try:
                df, is_copied = self.apply_decimator(
                    t.cast(pd.DataFrame, df),
                    x_column,
                    y_column,
                    z_column,
                    payload=decimator_payload,
                    is_copied=is_copied,
                )
                is_decimator_applied = True
            except Exception as e:
                _warn(f"Limit rows error with {decimator_var_name} for Dataframe", e)
        # only include columns involving the decimator
        if filter_unused_columns:
            filterd_columns = [x_column, y_column, z_column] if z_column else [x_column, y_column]
            df = df.filter(filterd_columns, axis=1)
        return df, is_decimator_applied, is_copied

    def on_decimate(
        self,
        df: pd.DataFrame,
        decimator_instance_payload: t.Dict[str, t.Any],
        decimator_payload: t.Dict[str, t.Any],
        is_copied: bool = False,
        filter_unused_columns: bool = True,
    ):
        """This function is executed whenever a decimator is found during runtime.

        Users can override this function by providing an alternate implementation inside the constructor
        to provide custom decimation logic.

        Arguments:
            df (pandas.DataFrame): The DataFrame that will be decimated.
            decimator_instance_payload (Dict[str, any]): The payload for the current instance of decimator. Each
                decimation request might contain multiple decimators to handle multiple traces.
            decimator_payload (Dict[str, any]): The full decimator payload including the current decimator.
            is_copied (bool): A flag to indicate if the DataFrame is copied.
            filter_unused_columns (bool): A flag to indicate if the DataFrame columns should be filtered to only
                include the columns that are involved with the decimator.

        Returns:
            A tuple containing the decimated DataFrame, a flag indicating if the decimator is applied,
            and a flag indicating if the DataFrame was copied.
        """
        if self.__user_defined_on_decimate and callable(self.__user_defined_on_decimate):
            try:
                return self.__user_defined_on_decimate(
                    df, decimator_instance_payload, decimator_payload, is_copied, filter_unused_columns
                )
            except Exception as e:
                _warn("Error executing user defined on_decimate function: ", e)
        return self._on_decimate_df(df, decimator_instance_payload, decimator_payload, filter_unused_columns)

    def apply_decimator(
        self,
        dataframe: pd.DataFrame,
        x_column_name: t.Optional[str],
        y_column_name: str,
        z_column_name: str,
        payload: t.Dict[str, t.Any],
        is_copied: bool,
    ):
        """This function is executed whenever a decimator is applied to the data.

        This function is used by default the `on_decimate` function.
        Users can override this function by providing an alternate function inside the constructor
        to provide custom handling only when the decimator is applied. This avoids the need to override
        the default `on_decimate` handling logic.

        Arguments:
            dataframe (pandas.DataFrame): The DataFrame that will be decimated.
            x_column_name (Optional[str]): The name of the x-axis column.
            y_column_name (str): The name of the y-axis column.
            z_column_name (str): The name of the z-axis column.
            payload (Dict[str, any]): The payload for the current decimator.
            is_copied (bool): A flag to indicate if the DataFrame is copied.

        Returns:
            A tuple containing the decimated DataFrame and a flag indicating if the DataFrame was copied
        """
        if self.__user_defined_apply_decimator and callable(self.__user_defined_apply_decimator):
            try:
                return self.__user_defined_apply_decimator(
                    dataframe, x_column_name, y_column_name, z_column_name, payload, is_copied
                )
            except Exception as e:
                _warn("Error executing user defined apply_decimator function: ", e)
        return self._df_apply_decimator(dataframe, x_column_name, y_column_name, z_column_name, payload, is_copied)

    @abstractmethod
    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        """Decimate function.

        This method is executed when the appropriate conditions specified in the
        constructor are met. This function implements the algorithm that determines
        which data points are kept or dropped.

        Arguments:
            data (numpy.array): An array containing all the data points represented as
                tuples.
            payload (Dict[str, any]): additional information on charts that is provided
                at runtime.

        Returns:
            An array of Boolean mask values. The array should set True or False for each
                of its indexes where True indicates that the corresponding data point
                from *data* should be preserved, or False requires that this
                data point be dropped.
        """
        raise NotImplementedError
