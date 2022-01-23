from __future__ import annotations

import typing as t

import numpy as np
from rdp import rdp

if t.TYPE_CHECKING:
    import pandas as pd


def df_data_filter(
    dataframe: pd.DataFrame,
    x_column_name: t.Union[None, str],
    y_column_name: str,
    expected_row_count: t.Union[None, int],
    margin_of_error: float = 0.3,
) -> t.Tuple[pd.DataFrame, t.Union[None, str], str]:
    if expected_row_count is not None and df_row_count(dataframe) <= expected_row_count * (1 + margin_of_error):
        return dataframe, x_column_name, y_column_name
    df = dataframe.copy()
    if not x_column_name:
        x_column_name = "tAiPy_index"
        df[x_column_name] = df.index
    if expected_row_count is None:
        expected_row_count = int(df_row_count(df) * 0.1)
    points = df[[x_column_name, y_column_name]].to_numpy()
    return df[np_filter(points, int(expected_row_count), margin_of_error)], x_column_name, y_column_name


def np_filter(points: np.ndarray, expected_row_count: int, margin_of_error: float) -> np.ndarray:
    # Perform binary search to find the appropriate epsilon for rdp algorithm
    # epsilon will determine number of rows in dataframe
    upper_epsilon = round(np.diff(points[:, 1]).max())
    print(upper_epsilon)
    lower_epsilon = 0
    epsilon = 50  # good starting point for epsilon
    upper_count = (1 + margin_of_error) * expected_row_count
    lower_count = (1 - margin_of_error) * expected_row_count
    result = rdp(points, epsilon=epsilon, return_mask=True)
    count = np.count_nonzero(result)
    # The search will end if the number of rows fits within this `count` range or `upper_epsilon` is smaller than `lower_epsilon`
    while upper_epsilon > lower_epsilon and (count > upper_count or count < lower_count):
        if count > expected_row_count:
            lower_epsilon = epsilon + 1
        else:
            upper_epsilon = epsilon - 1
        epsilon = round((upper_epsilon + lower_epsilon) / 2)
        result = rdp(points, epsilon=epsilon, return_mask=True)
        count = np.count_nonzero(result)
    return result


def df_row_count(df: pd.DataFrame) -> int:
    return df.shape[0]
