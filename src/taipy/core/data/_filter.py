# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from collections.abc import Hashable
from functools import reduce
from operator import and_, or_
from typing import Dict, Iterable, List, Tuple, Union

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
from pandas.core.common import is_bool_indexer

from .operator import JoinOperator, Operator


class _FilterDataNode:
    __DATAFRAME_DATA_TYPE = "dataframe"
    __MULTI_SHEET_EXCEL_DATA_TYPE = "multi_sheet_excel"
    __CUSTOM_DATA_TYPE = "custom"

    def __init__(self, data_node_id, data: Union[pd.DataFrame, modin_pd.DataFrame, List]) -> None:
        self.data_node_id = data_node_id
        self.data = data
        self.data_type = None
        if self._is_pandas_object():
            self.data_type = self.__DATAFRAME_DATA_TYPE
        elif self.is_multi_sheet_excel():
            self.data_type = self.__MULTI_SHEET_EXCEL_DATA_TYPE
        else:
            self.data_type = self.__CUSTOM_DATA_TYPE

    def _is_pandas_object(self) -> bool:
        return isinstance(self.data, (pd.DataFrame, modin_pd.DataFrame)) or isinstance(
            self.data, (pd.Series, modin_pd.DataFrame)
        )

    def is_multi_sheet_excel(self) -> bool:
        if isinstance(self.data, Dict):
            has_df_children = all([isinstance(e, (pd.DataFrame, modin_pd.DataFrame)) for e in self.data.values()])
            has_list_children = all([isinstance(e, List) for e in self.data.values()])
            return has_df_children or has_list_children
        return False

    def data_is_dataframe(self) -> bool:
        return self.data_type == self.__DATAFRAME_DATA_TYPE

    def data_is_multi_sheet_excel(self) -> bool:
        return self.data_type == self.__MULTI_SHEET_EXCEL_DATA_TYPE

    def __getitem__(self, key):
        if isinstance(key, _FilterDataNode):
            key = key.data
        if isinstance(key, Hashable):
            filtered_data = self.__getitem_hashable(key)
        elif isinstance(key, slice):
            filtered_data = self.__getitem_slice(key)
        elif isinstance(key, (pd.DataFrame, modin_pd.DataFrame)):
            filtered_data = self.__getitem_dataframe(key)
        elif is_bool_indexer(key):
            filtered_data = self.__getitem_bool_indexer(key)
        elif isinstance(key, Iterable):
            filtered_data = self.__getitem_iterable(key)
        else:
            filtered_data = None
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __getitem_hashable(self, key):
        if self.data_is_dataframe() or self.data_is_multi_sheet_excel():
            return self.data.get(key)
        return [getattr(e, key) for e in self.data]

    def __getitem_slice(self, key):
        return self.data[key]

    def __getitem_dataframe(self, key: Union[pd.DataFrame, modin_pd.DataFrame]):
        if self.data_is_dataframe():
            return self.data[key]
        if self.data_is_list_of_dict():
            filtered_data = list()
            for i, row in key.iterrows():
                filtered_row = dict()
                for col in row.index:
                    filtered_row[col] = self.data[i][col] if row[col] else None
                filtered_data.append(filtered_row)
            return filtered_data
        return None

    def data_is_list_of_dict(self) -> bool:
        return all(isinstance(x, Dict) for x in self.data)

    def __getitem_bool_indexer(self, key):
        if self.data_is_dataframe():
            return self.data[key]
        return [e for i, e in enumerate(self.data) if key[i]]

    def __getitem_iterable(self, keys):
        if self.data_is_dataframe():
            return self.data[keys]
        filtered_data = []
        for e in self.data:
            filtered_data.append({k: getattr(e, k) for k in keys})
        return filtered_data

    @staticmethod
    def _filter_dataframe(
        df_data: Union[pd.DataFrame, modin_pd.DataFrame], operators: Union[List, Tuple], join_operator=JoinOperator.AND
    ):
        filtered_df_data = []
        if join_operator == JoinOperator.AND:
            how = "inner"
        elif join_operator == JoinOperator.OR:
            how = "outer"
        else:
            return NotImplementedError
        for key, value, operator in operators:
            filtered_df_data.append(_FilterDataNode._filter_dataframe_per_key_value(df_data, key, value, operator))
        return _FilterDataNode.__dataframe_merge(filtered_df_data, how) if filtered_df_data else pd.DataFrame()

    @staticmethod
    def _filter_dataframe_per_key_value(
        df_data: Union[pd.DataFrame, modin_pd.DataFrame], key: str, value, operator: Operator
    ):
        df_by_col = df_data[key]
        if operator == Operator.EQUAL:
            df_by_col = df_by_col == value
        if operator == Operator.NOT_EQUAL:
            df_by_col = df_by_col != value
        if operator == Operator.LESS_THAN:
            df_by_col = df_by_col < value
        if operator == Operator.LESS_OR_EQUAL:
            df_by_col = df_by_col <= value
        if operator == Operator.GREATER_THAN:
            df_by_col = df_by_col > value
        if operator == Operator.GREATER_OR_EQUAL:
            df_by_col = df_by_col >= value
        return df_data[df_by_col]

    @staticmethod
    def __dataframe_merge(df_list: List, how="inner"):
        return reduce(lambda df1, df2: pd.merge(df1, df2, how=how), df_list)

    @staticmethod
    def _filter_numpy_array(data: np.ndarray, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        conditions = []
        for key, value, operator in operators:
            conditions.append(_FilterDataNode.__get_filter_condition_per_key_value(data, key, value, operator))

        if join_operator == JoinOperator.AND:
            join_conditions = reduce(and_, conditions)
        elif join_operator == JoinOperator.OR:
            join_conditions = reduce(or_, conditions)
        else:
            return NotImplementedError

        return data[join_conditions]

    @staticmethod
    def __get_filter_condition_per_key_value(array_data: np.ndarray, key, value, operator: Operator):
        if not isinstance(key, int):
            key = int(key)

        if operator == Operator.EQUAL:
            return array_data[:, key] == value
        if operator == Operator.NOT_EQUAL:
            return array_data[:, key] != value
        if operator == Operator.LESS_THAN:
            return array_data[:, key] < value
        if operator == Operator.LESS_OR_EQUAL:
            return array_data[:, key] <= value
        if operator == Operator.GREATER_THAN:
            return array_data[:, key] > value
        if operator == Operator.GREATER_OR_EQUAL:
            return array_data[:, key] >= value

        return NotImplementedError

    @staticmethod
    def _filter_list(list_data: List, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        filtered_list_data = []
        for key, value, operator in operators:
            filtered_list_data.append(_FilterDataNode._filter_list_per_key_value(list_data, key, value, operator))
        if len(filtered_list_data) == 0:
            return filtered_list_data
        if join_operator == JoinOperator.AND:
            return _FilterDataNode.__list_intersect(filtered_list_data)
        elif join_operator == JoinOperator.OR:
            return list(set(np.concatenate(filtered_list_data)))
        else:
            return NotImplementedError

    @staticmethod
    def _filter_list_per_key_value(list_data: List, key: str, value, operator: Operator):
        filtered_list = []
        for row in list_data:
            row_value = getattr(row, key, None)
            if row_value is None:
                continue

            if operator == Operator.EQUAL and row_value == value:
                filtered_list.append(row)
            if operator == Operator.NOT_EQUAL and row_value != value:
                filtered_list.append(row)
            if operator == Operator.LESS_THAN and row_value < value:
                filtered_list.append(row)
            if operator == Operator.LESS_OR_EQUAL and row_value <= value:
                filtered_list.append(row)
            if operator == Operator.GREATER_THAN and row_value > value:
                filtered_list.append(row)
            if operator == Operator.GREATER_OR_EQUAL and row_value >= value:
                filtered_list.append(row)
        return filtered_list

    @staticmethod
    def __list_intersect(list_data):
        return list(set(list_data.pop()).intersection(*map(set, list_data)))
