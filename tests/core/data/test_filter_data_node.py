from typing import Dict, List

import numpy as np
import pandas as pd

from taipy.core.data.data_node import DataNode
from taipy.core.data.filter import FilterDataNode


class FakeDataframeDataNode(DataNode):
    COLUMN_NAME_1 = "a"
    COLUMN_NAME_2 = "b"

    def __init__(self, config_name, default_data_frame, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = default_data_frame

    def _read(self):
        return self.data


class CustomClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class FakeCustomDataNode(DataNode):
    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = [CustomClass(i, i * 2) for i in range(10)]

    def _read(self):
        return self.data


class FakeMultiSheetExcelDataFrameDataNode(DataNode):
    def __init__(self, config_name, default_data_frame, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = {
            "Sheet1": default_data_frame,
            "Sheet2": default_data_frame,
        }

    def _read(self):
        return self.data


class FakeMultiSheetExcelCustomDataNode(DataNode):
    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = {
            "Sheet1": [CustomClass(i, i * 2) for i in range(10)],
            "Sheet2": [CustomClass(i, i * 2) for i in range(10)],
        }

    def _read(self):
        return self.data


class TestFilterDataNode:
    def test_get_item(self, default_data_frame):

        # get item for DataFrame data_type
        default_data_frame[1] = [100, 100]
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert len(filtered_df_dn.data) == len(default_data_frame["a"])
        assert filtered_df_dn.data.to_dict() == default_data_frame["a"].to_dict()

        filtered_df_dn = df_dn[1]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert len(filtered_df_dn.data) == len(default_data_frame[1])
        assert filtered_df_dn.data.to_dict() == default_data_frame[1].to_dict()

        filtered_df_dn = df_dn[0:2]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert filtered_df_dn.data.shape == default_data_frame[0:2].shape
        assert len(filtered_df_dn.data) == 2

        bool_df = default_data_frame.copy(deep=True) > 4
        filtered_df_dn = df_dn[bool_df]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)

        bool_1d_index = [True, False]
        filtered_df_dn = df_dn[bool_1d_index]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert filtered_df_dn.data.to_dict() == default_data_frame[bool_1d_index].to_dict()
        assert len(filtered_df_dn.data) == 1

        filtered_df_dn = df_dn[["a", "b"]]
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert filtered_df_dn.data.shape == default_data_frame[["a", "b"]].shape
        assert filtered_df_dn.data.to_dict() == default_data_frame[["a", "b"]].to_dict()

        # get item for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert len(filtered_custom_dn.data) == 10
        assert filtered_custom_dn.data == [i for i in range(10)]

        filtered_custom_dn = custom_dn[0:5]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, CustomClass) for x in filtered_custom_dn.data])
        assert len(filtered_custom_dn.data) == 5

        bool_df = pd.DataFrame({"a": [i for i in range(10)], "b": [i * 2 for i in range(10)]}) > 4
        filtered_custom_dn = custom_dn[["a", "b"]][bool_df]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, Dict) for x in filtered_custom_dn.data])
        for i, row in bool_df.iterrows():
            for col in row.index:
                print(i, col, row[col])
                if row[col]:
                    assert filtered_custom_dn.data[i][col] == custom_dn[["a", "b"]].data[i][col]
                else:
                    assert filtered_custom_dn.data[i][col] is None

        filtered_custom_dn = custom_dn["a"][bool_df]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert filtered_custom_dn.data is None

        filtered_custom_dn = custom_dn[0:10][bool_df]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert filtered_custom_dn.data is None

        bool_1d_index = [True if i < 5 else False for i in range(10)]
        filtered_custom_dn = custom_dn[bool_1d_index]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert len(filtered_custom_dn.data) == 5
        assert filtered_custom_dn.data == custom_dn._read()[:5]

        filtered_custom_dn = custom_dn[["a", "b"]]
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, Dict) for x in filtered_custom_dn.data])
        assert len(filtered_custom_dn.data) == 10
        assert filtered_custom_dn.data == [{"a": i, "b": i * 2} for i in range(10)]

        # get item for Multi-sheet Excel data_type
        multi_sheet_excel_df_dn = FakeMultiSheetExcelDataFrameDataNode(
            "fake multi-sheet excel df dn", default_data_frame
        )
        filtered_multi_sheet_excel_df_dn = multi_sheet_excel_df_dn["Sheet1"]
        assert isinstance(filtered_multi_sheet_excel_df_dn, FilterDataNode)
        assert isinstance(filtered_multi_sheet_excel_df_dn.data, pd.DataFrame)
        assert len(filtered_multi_sheet_excel_df_dn.data) == len(default_data_frame)
        assert np.array_equal(filtered_multi_sheet_excel_df_dn.data.to_numpy(), default_data_frame.to_numpy())

        multi_sheet_excel_custom_dn = FakeMultiSheetExcelCustomDataNode("fake multi-sheet excel custom dn")
        filtered_multi_sheet_excel_custom_dn = multi_sheet_excel_custom_dn["Sheet1"]
        assert isinstance(filtered_multi_sheet_excel_custom_dn, FilterDataNode)
        assert isinstance(filtered_multi_sheet_excel_custom_dn.data, List)
        assert len(filtered_multi_sheet_excel_custom_dn.data) == 10
        expected_value = [CustomClass(i, i * 2) for i in range(10)]
        assert all(
            [
                expected.a == filtered.a and expected.b == filtered.b
                for expected, filtered in zip(expected_value, filtered_multi_sheet_excel_custom_dn.data)
            ]
        )

    def test_equal(self, default_data_frame):
        # equal to for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] == 1
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] == 1))

        filtered_df_dn = df_dn[["a", "b"]] == 1
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] == 1))

        # equal to for custom list data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] == 0
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [True] + [False for _ in range(9)]

        filtered_custom_dn = custom_dn[["a", "b"]] == 0
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [False for _ in range(10)]

    def test_not_equal(self, default_data_frame):
        # not equal to for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] != 1
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] != 1))

        filtered_df_dn = df_dn[["a", "b"]] != 1
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] != 1))

        # not equal to for custom list data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] != 0
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [False] + [True for _ in range(9)]

        filtered_custom_dn = custom_dn[["a", "b"]] != 0
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [True for _ in range(10)]

    def test_larger_than(self, default_data_frame):
        # larger than for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] > 2
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] > 2))

        filtered_df_dn = df_dn[["a", "b"]] > 2
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] > 2))

        # larger than for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] > 5
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [False for _ in range(6)] + [True for _ in range(4)]

    def test_larger_equal_to(self, default_data_frame):
        # larger than or equal to for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] >= 4
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] >= 4))

        filtered_df_dn = df_dn[["a", "b"]] >= 4
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] >= 4))

        # larger than or equal to for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] >= 5
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [False for _ in range(5)] + [True for _ in range(5)]

    def test_lesser_than(self, default_data_frame):
        # lesser than for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] < 5
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] < 5))

        filtered_df_dn = df_dn[["a", "b"]] < 5
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] < 5))

        # lesser than for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] < 5
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [True for _ in range(5)] + [False for _ in range(5)]

    def test_lesser_equal_to(self, default_data_frame):
        # lesser than or equal to for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = df_dn["a"] <= 5
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] <= 5))

        filtered_df_dn = df_dn[["a", "b"]] <= 5
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] <= 5))

        # lesser than or equal to for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = custom_dn["a"] <= 5
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [True for _ in range(6)] + [False for _ in range(4)]

    def test_and(self, default_data_frame):
        # and comparator for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = (df_dn["a"] >= 2) & (df_dn["a"] <= 5)
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] >= 2) & (default_data_frame["a"] <= 5))

        filtered_df_dn = (df_dn[["a", "b"]] >= 2) & (df_dn[["a", "b"]] <= 5)
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] >= 2) & (default_data_frame[["a", "b"]] <= 5))

        # and comparator for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = (custom_dn["a"] >= 2) & (custom_dn["a"] <= 5)
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [False for _ in range(2)] + [True for _ in range(4)] + [
            False for _ in range(4)
        ]

    def test_or(self, default_data_frame):
        # or comparator for pandas dataframe data_type
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

        filtered_df_dn = (df_dn["a"] < 2) | (df_dn["a"] > 5)
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.Series)
        assert filtered_df_dn.data.dtype == bool
        assert all(filtered_df_dn.data == (default_data_frame["a"] < 2) | (default_data_frame["a"] > 5))

        filtered_df_dn = (df_dn[["a", "b"]] < 2) | (df_dn[["a", "b"]] > 5)
        assert isinstance(filtered_df_dn, FilterDataNode)
        assert isinstance(filtered_df_dn.data, pd.DataFrame)
        assert all(filtered_df_dn.data.dtypes == bool)
        assert all(filtered_df_dn.data == (default_data_frame[["a", "b"]] < 2) | (default_data_frame[["a", "b"]] > 5))

        # or comparator for custom data_type
        custom_dn = FakeCustomDataNode("fake custom dn")

        filtered_custom_dn = (custom_dn["a"] < 2) | (custom_dn["a"] > 5)
        assert isinstance(filtered_custom_dn, FilterDataNode)
        assert isinstance(filtered_custom_dn.data, List)
        assert all([isinstance(x, bool) for x in filtered_custom_dn.data])
        assert filtered_custom_dn.data == [True for _ in range(2)] + [False for _ in range(4)] + [
            True for _ in range(4)
        ]

    def test_to_string(self):
        filter_dn = FilterDataNode("dn_id", [])
        assert isinstance(str(filter_dn), str)
