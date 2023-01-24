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
from typing import Dict, Iterable, List, Union

import modin.pandas as modin_pd
import pandas as pd
from pandas.core.common import is_bool_indexer


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

    def __eq__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data == value
        else:
            filtered_data = [e == value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __lt__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data < value
        else:
            filtered_data = [e < value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __le__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data <= value
        else:
            filtered_data = [e <= value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __gt__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data > value
        else:
            filtered_data = [e > value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __ge__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data >= value
        else:
            filtered_data = [e >= value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __ne__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data != value
        else:
            filtered_data = [e != value for e in self.data]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __and__(self, other):
        if self.data_is_dataframe():
            if other.data_is_dataframe():
                filtered_data = self.data & other.data
            else:
                raise NotImplementedError
        else:
            if other.data_is_dataframe():
                raise NotImplementedError
            else:
                filtered_data = [s and o for s, o in zip(self.data, other.data)]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __or__(self, other):
        if self.data_is_dataframe():
            if other.data_is_dataframe():
                filtered_data = self.data | other.data
            else:
                raise NotImplementedError
        else:
            if other.data_is_dataframe():
                raise NotImplementedError
            else:
                filtered_data = [s or o for s, o in zip(self.data, other.data)]
        return _FilterDataNode(self.data_node_id, filtered_data)

    def __str__(self) -> str:
        if self.data_is_dataframe():
            return str(self.data)
        list_to_string = ""
        for e in self.data:
            list_to_string += str(e) + "\n"
        return list_to_string
