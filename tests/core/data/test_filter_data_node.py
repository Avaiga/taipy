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

from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

from taipy.core.data.operator import JoinOperator, Operator

from .utils import (
    CustomClass,
    FakeCustomDataNode,
    FakeDataframeDataNode,
    FakeDataNode,
    FakeListDataNode,
    FakeMultiSheetExcelCustomDataNode,
    FakeMultiSheetExcelDataFrameDataNode,
    FakeNumpyarrayDataNode,
)


def test_filter_pandas_exposed_type(default_data_frame):
    dn = FakeDataNode("fake_dn")
    dn.write("Any data")

    with pytest.raises(NotImplementedError):
        dn.filter((("any", 0, Operator.EQUAL)), JoinOperator.OR)
    with pytest.raises(NotImplementedError):
        dn.filter((("any", 0, Operator.NOT_EQUAL)), JoinOperator.OR)
    with pytest.raises(NotImplementedError):
        dn.filter((("any", 0, Operator.LESS_THAN)), JoinOperator.AND)
    with pytest.raises(NotImplementedError):
        dn.filter((("any", 0, Operator.LESS_OR_EQUAL)), JoinOperator.AND)
    with pytest.raises(NotImplementedError):
        dn.filter((("any", 0, Operator.GREATER_THAN)))
    with pytest.raises(NotImplementedError):
        dn.filter(("any", 0, Operator.GREATER_OR_EQUAL))

    df_dn = FakeDataframeDataNode("fake_dataframe_dn", default_data_frame)

    COLUMN_NAME_1 = "a"
    COLUMN_NAME_2 = "b"
    assert len(df_dn.filter((COLUMN_NAME_1, 1, Operator.EQUAL))) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
    )
    assert len(df_dn.filter((COLUMN_NAME_1, 1, Operator.NOT_EQUAL))) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.EQUAL)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.NOT_EQUAL)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.LESS_THAN)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] < 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.LESS_OR_EQUAL)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] <= 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.GREATER_THAN)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] > 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.GREATER_OR_EQUAL)])) == len(
        default_data_frame[default_data_frame[COLUMN_NAME_1] >= 1]
    )
    assert len(df_dn.filter([(COLUMN_NAME_1, -1000, Operator.LESS_OR_EQUAL)])) == 0
    assert len(df_dn.filter([(COLUMN_NAME_1, 1000, Operator.GREATER_OR_EQUAL)])) == 0
    assert len(df_dn.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_1, 5, Operator.EQUAL)])) == len(
        default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) & (default_data_frame[COLUMN_NAME_1] == 5)]
    )
    assert len(
        df_dn.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_2, 5, Operator.EQUAL)], JoinOperator.OR)
    ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) | (default_data_frame[COLUMN_NAME_2] == 5)])
    assert len(
        df_dn.filter(
            [(COLUMN_NAME_1, 1, Operator.GREATER_THAN), (COLUMN_NAME_2, 3, Operator.GREATER_THAN)], JoinOperator.AND
        )
    ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 1) & (default_data_frame[COLUMN_NAME_2] > 3)])
    assert len(
        df_dn.filter(
            [(COLUMN_NAME_1, 2, Operator.GREATER_THAN), (COLUMN_NAME_1, 3, Operator.GREATER_THAN)], JoinOperator.OR
        )
    ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 2) | (default_data_frame[COLUMN_NAME_1] > 3)])
    assert len(
        df_dn.filter(
            [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.AND
        )
    ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)])
    assert len(
        df_dn.filter(
            [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.OR
        )
    ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)])


def test_filter_list():
    list_dn = FakeListDataNode("fake_list_dn")

    KEY_NAME = "value"

    assert len(list_dn.filter((KEY_NAME, 4, Operator.EQUAL))) == 1
    assert len(list_dn.filter((KEY_NAME, 4, Operator.NOT_EQUAL))) == 9
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL)])) == 1
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.NOT_EQUAL)])) == 9
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.LESS_THAN)])) == 4
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.LESS_OR_EQUAL)])) == 5
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.GREATER_THAN)])) == 5
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.GREATER_OR_EQUAL)])) == 6
    assert len(list_dn.filter([(KEY_NAME, -1000, Operator.LESS_OR_EQUAL)])) == 0
    assert len(list_dn.filter([(KEY_NAME, 1000, Operator.GREATER_OR_EQUAL)])) == 0

    assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)])) == 0
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)], JoinOperator.OR)) == 2
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.AND)) == 0
    assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.OR)) == 1

    assert (
        len(list_dn.filter([(KEY_NAME, -10, Operator.LESS_OR_EQUAL), (KEY_NAME, 11, Operator.GREATER_OR_EQUAL)])) == 0
    )
    assert (
        len(
            list_dn.filter(
                [
                    (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                    (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                ],
                JoinOperator.AND,
            )
        )
        == 4
    )
    assert (
        len(
            list_dn.filter(
                [
                    (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                    (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                    (KEY_NAME, 11, Operator.EQUAL),
                ],
                JoinOperator.AND,
            )
        )
        == 0
    )
    assert (
        len(
            list_dn.filter(
                [
                    (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                    (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                    (KEY_NAME, 11, Operator.EQUAL),
                ],
                JoinOperator.OR,
            )
        )
        == 6
    )


def test_filter_numpy_exposed_type(default_data_frame):
    default_array = default_data_frame.to_numpy()

    df_dn = FakeNumpyarrayDataNode("fake_dataframe_dn", default_array)

    assert len(df_dn.filter((0, 1, Operator.EQUAL))) == len(default_array[default_array[:, 0] == 1])
    assert len(df_dn.filter((0, 1, Operator.NOT_EQUAL))) == len(default_array[default_array[:, 0] != 1])
    assert len(df_dn.filter([(0, 1, Operator.EQUAL)])) == len(default_array[default_array[:, 0] == 1])
    assert len(df_dn.filter([(0, 1, Operator.NOT_EQUAL)])) == len(default_array[default_array[:, 0] != 1])
    assert len(df_dn.filter([(0, 1, Operator.LESS_THAN)])) == len(default_array[default_array[:, 0] < 1])
    assert len(df_dn.filter([(0, 1, Operator.LESS_OR_EQUAL)])) == len(default_array[default_array[:, 0] <= 1])
    assert len(df_dn.filter([(0, 1, Operator.GREATER_THAN)])) == len(default_array[default_array[:, 0] > 1])
    assert len(df_dn.filter([(0, 1, Operator.GREATER_OR_EQUAL)])) == len(default_array[default_array[:, 0] >= 1])
    assert len(df_dn.filter([(0, -1000, Operator.LESS_OR_EQUAL)])) == 0
    assert len(df_dn.filter([(0, 1000, Operator.GREATER_OR_EQUAL)])) == 0
    assert len(df_dn.filter([(0, 4, Operator.EQUAL), (0, 5, Operator.EQUAL)])) == len(
        default_array[(default_array[:, 0] == 4) & (default_array[:, 0] == 5)]
    )
    assert len(df_dn.filter([(0, 4, Operator.EQUAL), (1, 5, Operator.EQUAL)], JoinOperator.OR)) == len(
        default_array[(default_array[:, 0] == 4) | (default_array[:, 1] == 5)]
    )
    assert len(df_dn.filter([(0, 1, Operator.GREATER_THAN), (1, 3, Operator.GREATER_THAN)], JoinOperator.AND)) == len(
        default_array[(default_array[:, 0] > 1) & (default_array[:, 1] > 3)]
    )
    assert len(df_dn.filter([(0, 2, Operator.GREATER_THAN), (0, 3, Operator.GREATER_THAN)], JoinOperator.OR)) == len(
        default_array[(default_array[:, 0] > 2) | (default_array[:, 0] > 3)]
    )
    assert len(df_dn.filter([(0, 10, Operator.GREATER_THAN), (0, -10, Operator.LESS_THAN)], JoinOperator.AND)) == len(
        default_array[(default_array[:, 0] > 10) | (default_array[:, 0] < -10)]
    )
    assert len(df_dn.filter([(0, 10, Operator.GREATER_THAN), (0, -10, Operator.LESS_THAN)], JoinOperator.OR)) == len(
        default_array[(default_array[:, 0] > 10) | (default_array[:, 0] < -10)]
    )


def test_filter_by_get_item(default_data_frame):
    # get item for DataFrame data_type
    default_data_frame[1] = [100, 100]
    df_dn = FakeDataframeDataNode("fake_dataframe_dn", default_data_frame)

    filtered_df_dn = df_dn["a"]
    assert isinstance(filtered_df_dn, pd.Series)
    assert len(filtered_df_dn) == len(default_data_frame["a"])
    assert filtered_df_dn.to_dict() == default_data_frame["a"].to_dict()

    filtered_df_dn = df_dn[1]
    assert isinstance(filtered_df_dn, pd.Series)
    assert len(filtered_df_dn) == len(default_data_frame[1])
    assert filtered_df_dn.to_dict() == default_data_frame[1].to_dict()

    filtered_df_dn = df_dn[0:2]
    assert isinstance(filtered_df_dn, pd.DataFrame)
    assert filtered_df_dn.shape == default_data_frame[0:2].shape
    assert len(filtered_df_dn) == 2

    bool_df = default_data_frame.copy(deep=True) > 4
    filtered_df_dn = df_dn[bool_df]
    assert isinstance(filtered_df_dn, pd.DataFrame)

    bool_1d_index = [True, False]
    filtered_df_dn = df_dn[bool_1d_index]
    assert isinstance(filtered_df_dn, pd.DataFrame)
    assert filtered_df_dn.to_dict() == default_data_frame[bool_1d_index].to_dict()
    assert len(filtered_df_dn) == 1

    filtered_df_dn = df_dn[["a", "b"]]
    assert isinstance(filtered_df_dn, pd.DataFrame)
    assert filtered_df_dn.shape == default_data_frame[["a", "b"]].shape
    assert filtered_df_dn.to_dict() == default_data_frame[["a", "b"]].to_dict()

    # get item for custom data_type
    custom_dn = FakeCustomDataNode("fake_custom_dn")

    filtered_custom_dn = custom_dn["a"]
    assert isinstance(filtered_custom_dn, List)
    assert len(filtered_custom_dn) == 10
    assert filtered_custom_dn == [i for i in range(10)]

    filtered_custom_dn = custom_dn[0:5]
    assert isinstance(filtered_custom_dn, List)
    assert all([isinstance(x, CustomClass) for x in filtered_custom_dn])
    assert len(filtered_custom_dn) == 5

    bool_1d_index = [True if i < 5 else False for i in range(10)]
    filtered_custom_dn = custom_dn[bool_1d_index]
    assert isinstance(filtered_custom_dn, List)
    assert len(filtered_custom_dn) == 5
    assert filtered_custom_dn == custom_dn._read()[:5]

    filtered_custom_dn = custom_dn[["a", "b"]]
    assert isinstance(filtered_custom_dn, List)
    assert all([isinstance(x, Dict) for x in filtered_custom_dn])
    assert len(filtered_custom_dn) == 10
    assert filtered_custom_dn == [{"a": i, "b": i * 2} for i in range(10)]

    # get item for Multi-sheet Excel data_type
    multi_sheet_excel_df_dn = FakeMultiSheetExcelDataFrameDataNode("fake_multi_sheet_excel_df_dn", default_data_frame)
    filtered_multi_sheet_excel_df_dn = multi_sheet_excel_df_dn["Sheet1"]
    assert isinstance(filtered_multi_sheet_excel_df_dn, pd.DataFrame)
    assert len(filtered_multi_sheet_excel_df_dn) == len(default_data_frame)
    assert np.array_equal(filtered_multi_sheet_excel_df_dn.to_numpy(), default_data_frame.to_numpy())

    multi_sheet_excel_custom_dn = FakeMultiSheetExcelCustomDataNode("fake_multi_sheet_excel_df_dn")
    filtered_multi_sheet_excel_custom_dn = multi_sheet_excel_custom_dn["Sheet1"]
    assert isinstance(filtered_multi_sheet_excel_custom_dn, List)
    assert len(filtered_multi_sheet_excel_custom_dn) == 10
    expected_value = [CustomClass(i, i * 2) for i in range(10)]
    assert all(
        [
            expected.a == filtered.a and expected.b == filtered.b
            for expected, filtered in zip(expected_value, filtered_multi_sheet_excel_custom_dn)
        ]
    )
