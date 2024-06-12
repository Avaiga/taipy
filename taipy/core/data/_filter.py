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

from collections.abc import Hashable
from functools import reduce
from itertools import chain
from operator import and_, or_
from typing import Dict, Iterable, List, Tuple, Union

import numpy as np
import pandas as pd
from pandas.core.common import is_bool_indexer

from .operator import JoinOperator, Operator


class _FilterDataNode:
    @staticmethod
    def __is_pandas_object(data) -> bool:
        return isinstance(data, (pd.DataFrame, pd.Series))

    @staticmethod
    def __is_multi_sheet_excel(data) -> bool:
        if isinstance(data, Dict):
            has_df_children = all(isinstance(e, pd.DataFrame) for e in data.values())
            has_list_children = all(isinstance(e, List) for e in data.values())
            has_np_array_children = all(isinstance(e, np.ndarray) for e in data.values())
            return has_df_children or has_list_children or has_np_array_children
        return False

    @staticmethod
    def __is_list_of_dict(data) -> bool:
        return all(isinstance(x, Dict) for x in data)

    @staticmethod
    def _filter_by_key(data, key):
        if isinstance(key, int):
            return _FilterDataNode.__getitem_int(data, key)

        if isinstance(key, slice) or (isinstance(key, tuple) and any(isinstance(e, slice) for e in key)):
            return _FilterDataNode.__getitem_slice(data, key)

        if isinstance(key, Hashable):
            return _FilterDataNode.__getitem_hashable(data, key)

        if isinstance(key, pd.DataFrame):
            return _FilterDataNode.__getitem_dataframe(data, key)

        if is_bool_indexer(key):
            return _FilterDataNode.__getitem_bool_indexer(data, key)

        if isinstance(key, Iterable):
            return _FilterDataNode.__getitem_iterable(data, key)

        return None

    @staticmethod
    def __getitem_int(data, key):
        return data[key]

    @staticmethod
    def __getitem_hashable(data, key):
        if _FilterDataNode.__is_pandas_object(data) or _FilterDataNode.__is_multi_sheet_excel(data):
            return data.get(key)
        return [getattr(entry, key, None) for entry in data]

    @staticmethod
    def __getitem_slice(data, key):
        return data[key]

    @staticmethod
    def __getitem_dataframe(data, key: pd.DataFrame):
        if _FilterDataNode.__is_pandas_object(data):
            return data[key]
        if _FilterDataNode.__is_list_of_dict(data):
            filtered_data = []
            for i, row in key.iterrows():
                filtered_row = {}
                for col in row.index:
                    filtered_row[col] = data[i][col] if row[col] else None
                filtered_data.append(filtered_row)
            return filtered_data
        return None

    @staticmethod
    def __getitem_bool_indexer(data, key):
        if _FilterDataNode.__is_pandas_object(data):
            return data[key]
        return [e for i, e in enumerate(data) if key[i]]

    @staticmethod
    def __getitem_iterable(data, keys):
        if _FilterDataNode.__is_pandas_object(data):
            return data[keys]

        return [{k: getattr(entry, k) for k in keys if hasattr(entry, k)} for entry in data]

    @staticmethod
    def _filter(data, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        if len(operators) == 0:
            return data

        if isinstance(data, Dict):
            return {k: _FilterDataNode._filter(v, operators, join_operator) for k, v in data.items()}

        if not isinstance(operators[0], (list, tuple)):
            if isinstance(data, pd.DataFrame):
                return _FilterDataNode.__filter_dataframe_per_key_value(data, operators[0], operators[1], operators[2])
            if isinstance(data, np.ndarray):
                list_operators = [operators]
                return _FilterDataNode.__filter_numpy_array(data, list_operators)
            if isinstance(data, List):
                return _FilterDataNode.__filter_list_per_key_value(data, operators[0], operators[1], operators[2])
        else:
            if isinstance(data, pd.DataFrame):
                return _FilterDataNode.__filter_dataframe(data, operators, join_operator=join_operator)
            if isinstance(data, np.ndarray):
                return _FilterDataNode.__filter_numpy_array(data, operators, join_operator=join_operator)
            if isinstance(data, List):
                return _FilterDataNode.__filter_list(data, operators, join_operator=join_operator)
        raise NotImplementedError

    @staticmethod
    def __filter_dataframe(df_data: pd.DataFrame, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        if join_operator == JoinOperator.AND:
            how = "inner"
        elif join_operator == JoinOperator.OR:
            how = "outer"
        else:
            raise NotImplementedError

        filtered_df_data = [
            _FilterDataNode.__filter_dataframe_per_key_value(df_data, key, value, operator)
            for key, value, operator in operators
        ]

        return _FilterDataNode.__dataframe_merge(filtered_df_data, how) if filtered_df_data else pd.DataFrame()

    @staticmethod
    def __filter_dataframe_per_key_value(df_data: pd.DataFrame, key: str, value, operator: Operator):
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
    def __filter_numpy_array(data: np.ndarray, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        conditions = [
            _FilterDataNode.__get_filter_condition_per_key_value(data, key, value, operator)
            for key, value, operator in operators
        ]

        if join_operator == JoinOperator.AND:
            join_conditions = reduce(and_, conditions)
        elif join_operator == JoinOperator.OR:
            join_conditions = reduce(or_, conditions)
        else:
            raise NotImplementedError

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

        raise NotImplementedError

    @staticmethod
    def __filter_list(list_data: List, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        filtered_list_data = [
            _FilterDataNode.__filter_list_per_key_value(list_data, key, value, operator)
            for key, value, operator in operators
        ]
        if not filtered_list_data:
            return filtered_list_data

        if join_operator == JoinOperator.AND:
            return _FilterDataNode.__list_intersect(filtered_list_data)
        elif join_operator == JoinOperator.OR:
            merged_list = list(chain.from_iterable(filtered_list_data))
            if all(isinstance(e, Dict) for e in merged_list):
                return list({frozenset(item.items()) for item in merged_list})
            return list(set(merged_list))
        else:
            raise NotImplementedError

    @staticmethod
    def __filter_list_per_key_value(list_data: List, key: str, value, operator: Operator):
        filtered_list = []
        for row in list_data:
            if isinstance(row, Dict):
                row_value = row.get(key, None)
            else:
                row_value = getattr(row, key, None)

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
