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

import csv
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd

from taipy.common.config.common.scope import Scope

from .._entity._reload import _Reloader
from .._version._version_manager_factory import _VersionManagerFactory
from ..job.job_id import JobId
from ._file_datanode_mixin import _FileDataNodeMixin
from ._tabular_datanode_mixin import _TabularDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class CSVDataNode(DataNode, _FileDataNodeMixin, _TabularDataNodeMixin):
    """Data Node stored as a CSV file.

    The *properties* attribute can contain the following optional entries:

    - *encoding* (`str`): The encoding of the CSV file. The default value is `utf-8`.
    - *default_path* (`str`): The default path of the CSV file used at the instantiation of the
        data node.
    - *default_data*: The default data of the data node. It is used at the data node instantiation
        to write the data to the CSV file.
    - *has_header* (`bool`): If True, indicates that the CSV file has a header.
    - *exposed_type*: The exposed type of the data read from CSV file. The default value is `pandas`.
    """

    __STORAGE_TYPE = "csv"
    __ENCODING_KEY = "encoding"

    _REQUIRED_PROPERTIES: List[str] = []

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: Optional[str] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Optional[Dict] = None,
    ) -> None:
        self.id = id or self._new_id(config_id)

        if properties is None:
            properties = {}

        if self.__ENCODING_KEY not in properties.keys():
            properties[self.__ENCODING_KEY] = "utf-8"

        if self._HAS_HEADER_PROPERTY not in properties.keys():
            properties[self._HAS_HEADER_PROPERTY] = True

        properties[self._EXPOSED_TYPE_PROPERTY] = _TabularDataNodeMixin._get_valid_exposed_type(properties)
        self._check_exposed_type(properties[self._EXPOSED_TYPE_PROPERTY])

        default_value = properties.pop(self._DEFAULT_DATA_KEY, None)
        _FileDataNodeMixin.__init__(self, properties)
        _TabularDataNodeMixin.__init__(self, **properties)

        DataNode.__init__(
            self,
            config_id,
            scope,
            self.id,
            owner_id,
            parent_ids,
            last_edit_date,
            edits,
            version or _VersionManagerFactory._build_manager()._get_latest_version(),
            validity_period,
            edit_in_progress,
            editor_id,
            editor_expiration_date,
            **properties,
        )

        with _Reloader():
            self._write_default_data(default_value)

        self._TAIPY_PROPERTIES.update(
            {
                self._PATH_KEY,
                self._DEFAULT_PATH_KEY,
                self._DEFAULT_DATA_KEY,
                self._IS_GENERATED_KEY,
                self._HAS_HEADER_PROPERTY,
                self._EXPOSED_TYPE_PROPERTY,
                self.__ENCODING_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def write_with_column_names(self, data: Any, columns: Optional[List[str]] = None, job_id: Optional[JobId] = None):
        """Write a selection of columns.

        Parameters:
            data (Any): The data to write.
            columns (Optional[List[str]]): The list of column names to write.
            job_id (JobId): An optional identifier of the writer.
        """
        self._write(data, columns)
        self.track_edit(timestamp=datetime.now(), job_id=job_id)

    def _read(self):
        return self._read_from_path()

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        if path is None:
            path = self._path

        properties = self.properties
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe(path=path)
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy(path=path)
        return self._read_as(path=path)

    def _read_as(self, path: str):
        properties = self.properties
        with open(path, encoding=properties[self.__ENCODING_KEY]) as csvFile:
            if properties[self._HAS_HEADER_PROPERTY]:
                reader_with_header = csv.DictReader(csvFile)
                return [self._decoder(line) for line in reader_with_header]

            reader_without_header = csv.reader(csvFile)
            return [self._decoder(line) for line in reader_without_header]

    def _read_as_numpy(self, path: str) -> np.ndarray:
        return self._read_as_pandas_dataframe(path=path).to_numpy()

    def _read_as_pandas_dataframe(
        self,
        path: str,
        usecols: Optional[List[int]] = None,
        column_names: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        try:
            properties = self.properties
            if properties[self._HAS_HEADER_PROPERTY]:
                if column_names:
                    return pd.read_csv(path, encoding=properties[self.__ENCODING_KEY])[column_names]
                return pd.read_csv(path, encoding=properties[self.__ENCODING_KEY])
            else:
                if usecols:
                    return pd.read_csv(path, encoding=properties[self.__ENCODING_KEY], header=None, usecols=usecols)
                return pd.read_csv(path, encoding=properties[self.__ENCODING_KEY], header=None)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def _append(self, data: Any):
        properties = self.properties
        exposed_type = properties[self._EXPOSED_TYPE_PROPERTY]
        data = self._convert_data_to_dataframe(exposed_type, data)
        data.to_csv(self._path, mode="a", index=False, encoding=properties[self.__ENCODING_KEY], header=False)

    def _write(self, data: Any, columns: Optional[List[str]] = None):
        properties = self.properties
        exposed_type = properties[self._EXPOSED_TYPE_PROPERTY]
        data = self._convert_data_to_dataframe(exposed_type, data)

        if columns and isinstance(data, pd.DataFrame):
            data.columns = pd.Index(columns, dtype="object")

        data.to_csv(
            self._path,
            index=False,
            encoding=properties[self.__ENCODING_KEY],
            header=properties[self._HAS_HEADER_PROPERTY],
        )
