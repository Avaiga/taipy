import collections
from typing import Dict, Iterable, List, Union

import pandas as pd
from pandas.core.common import is_bool_indexer


class FilterDataNode:
    __DATAFRAME_DATA_TYPE = "dataframe"
    __CUSTOM_DATA_TYPE = "custom"

    def __init__(self, data_node_id, data: Union[pd.DataFrame, List]) -> None:
        self.data_node_id = data_node_id
        self.data = data
        self.data_type = None
        if isinstance(self.data, pd.DataFrame) or isinstance(self.data, pd.Series):
            self.data_type = self.__DATAFRAME_DATA_TYPE
        else:
            self.data_type = self.__CUSTOM_DATA_TYPE

    def data_is_dataframe(self) -> bool:
        return self.data_type == self.__DATAFRAME_DATA_TYPE

    def __getitem__(self, key):
        if isinstance(key, FilterDataNode):
            key = key.data
        if isinstance(key, collections.Hashable):
            filtered_data = self.__getitem_hashable(key)
        elif isinstance(key, slice):
            filtered_data = self.__getitem_slice(key)
        elif isinstance(key, pd.DataFrame):
            filtered_data = self.__getitem_dataframe(key)
        elif is_bool_indexer(key):
            filtered_data = self.__getitem_bool_indexer(key)
        elif isinstance(key, Iterable):
            filtered_data = self.__getitem_iterable(key)
        else:
            filtered_data = None
        return FilterDataNode(self.data_node_id, filtered_data)

    def __getitem_hashable(self, key):
        if self.data_is_dataframe():
            return self.data.get(key)
        return [getattr(e, key) for e in self.data]

    def __getitem_slice(self, key):
        return self.data[key]

    def __getitem_dataframe(self, key: pd.DataFrame):
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

        # if self.data_is_list_of_dict():
        #     return self._reduce_on_key(
        #         key,
        #         collections.defaultdict(list),
        #         (lambda row, col, acc: acc[col].append(row[col])),
        #         (lambda row, col, acc: acc[col].append(None)),
        #     )
        # return self._reduce_on_key(key, [], (lambda row, col, acc: acc.append(row)))

    def data_is_list_of_dict(self) -> bool:
        return all(isinstance(x, Dict) for x in self.data)

    # def _reduce_on_key(self, key, acc, on_true, on_false=None):
    #     for col in key.columns:
    #         for i, row in enumerate(key[col]):
    #             if row:
    #                 on_true(self.data[i], col, acc)
    #             elif on_false:
    #                 on_false(self.data[i], col, acc)
    #     return acc

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
        return FilterDataNode(self.data_node_id, filtered_data)

    def __lt__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data < value
        else:
            filtered_data = [e < value for e in self.data]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __le__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data <= value
        else:
            filtered_data = [e <= value for e in self.data]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __gt__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data > value
        else:
            filtered_data = [e > value for e in self.data]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __ge__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data >= value
        else:
            filtered_data = [e >= value for e in self.data]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __ne__(self, value):
        if self.data_is_dataframe():
            filtered_data = self.data != value
        else:
            filtered_data = [e != value for e in self.data]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __and__(self, other):
        if self.data_is_dataframe():
            if other.data_is_dataframe():
                filtered_data = self.data & other.data
            else:
                return NotImplemented
        else:
            if other.data_is_dataframe():
                return NotImplemented
            else:
                filtered_data = [s and o for s, o in zip(self.data, other.data)]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __or__(self, other):
        if self.data_is_dataframe():
            if other.data_is_dataframe():
                filtered_data = self.data | other.data
            else:
                return NotImplemented
        else:
            if other.data_is_dataframe():
                return NotImplemented
            else:
                filtered_data = [s or o for s, o in zip(self.data, other.data)]
        return FilterDataNode(self.data_node_id, filtered_data)

    def __str__(self) -> str:
        if self.data_is_dataframe():
            return str(self.data)
        list_to_string = ""
        for e in self.data:
            list_to_string += str(e) + "\n"
        return list_to_string
