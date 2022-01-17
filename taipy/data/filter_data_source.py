from copy import deepcopy
from typing import Dict, Iterable, List, Union

import pandas as pd
from pandas.core.common import is_bool_indexer


class FilterDataSource:
    def __init__(self, data_source_id, data: Union[pd.DataFrame, List]) -> None:
        self.data_source_id = data_source_id
        self.data = data
        self.data_type = None
        if isinstance(self.data, pd.DataFrame) or isinstance(self.data, pd.Series):
            self.data_type = "dataframe"
        else:
            # TODO: current input: List, else??
            self.data_type = "custom"

    def __data_is_dataframe(self) -> bool:
        return self.data_type == "dataframe"

    def __getitem__(self, key):
        if FilterDataSource.__is_hashable(key):  # try hashable
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
        return FilterDataSource(self.data_source_id, filtered_data)

    @staticmethod
    def __is_hashable(value):
        try:
            hash(value)
        except TypeError:
            return False
        else:
            return True

    def __getitem_hashable(self, key):
        if self.__data_is_dataframe():
            if key in self.data.columns:
                return self.data[key]
        else:
            return [getattr(e, key) for e in self.data]

    def __getitem_slice(self, key):
        return self.data[key]

    def __getitem_dataframe(self, key: pd.DataFrame):
        if self.__data_is_dataframe():
            return self.data[key]

        filtered_data = deepcopy(self.data)
        has_dict_element = all(map(lambda x: isinstance(x, Dict), filtered_data))
        if has_dict_element:
            for col in key.columns:
                for i, row in enumerate(key[col]):
                    filtered_data[i][col] = filtered_data[i][col] if row else None
        else:
            for col in key.columns:
                for i, row in enumerate(key[col]):
                    setattr(filtered_data[i], col, getattr(filtered_data[i], col) if row else None)

        return filtered_data

    def __getitem_bool_indexer(self, key):
        if self.__data_is_dataframe():
            return self.data[key]
        return [e for i, e in enumerate(self.data) if key[i]]

    def __getitem_iterable(self, keys):
        if self.__data_is_dataframe():
            return self.data[keys]
        filtered_data = []
        for e in self.data:
            row = {}
            for k in keys:
                row[k] = getattr(e, k)
            filtered_data.append(row)
        return filtered_data

    def __eq__(self, value):
        if self.__data_is_dataframe():
            return self.data == value
        return [e == value for e in self.data]

    def __lt__(self, value):
        if self.__data_is_dataframe():
            return self.data < value
        return [e < value for e in self.data]

    def __le__(self, value):
        if self.__data_is_dataframe():
            return self.data <= value
        return [e <= value for e in self.data]

    def __gt__(self, value):
        if self.__data_is_dataframe():
            return self.data > value
        return [e > value for e in self.data]

    def __ge__(self, value):
        if self.__data_is_dataframe():
            return self.data >= value
        return [e >= value for e in self.data]

    def __ne__(self, value):
        if self.__data_is_dataframe():
            return self.data != value
        return [e != value for e in self.data]

    def __repr__(self) -> str:
        if self.__data_is_dataframe():
            return f"FilterDataSource ({repr(self.data)})"
        return f"FilterDataSource ({self.data})"

    def __str__(self) -> str:
        if self.__data_is_dataframe():
            return str(self.data)
        return str(self.data)
