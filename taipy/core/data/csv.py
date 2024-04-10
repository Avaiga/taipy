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

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..job.job_id import JobId
from ._file_datanode_mixin import _FileDataNodeMixin
from ._tabular_datanode_mixin import _TabularDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class CSVDataNode(DataNode, _FileDataNodeMixin, _TabularDataNodeMixin):
    """Data Node stored as a CSV file.

    Attributes:
        config_id (str): Identifier of the data node configuration. This string must be a valid
            Python identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        owner_id (str): The identifier of the owner (sequence_id, scenario_id, cycle_id) or `None`.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The duration implemented as a timedelta since the last edit date for
            which the data node can be considered up-to-date. Once the validity period has passed, the data node is
            considered stale and relevant tasks will run even if they are skippable (see the
            [Task management page](../core/entities/task-mgt.md) for more details).
            If _validity_period_ is set to `None`, the data node is always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        editor_id (Optional[str]): The identifier of the user who is currently editing the data node.
        editor_expiration_date (Optional[datetime]): The expiration date of the editor lock.
        path (str): The path to the CSV file.
        properties (dict[str, Any]): A dictionary of additional properties. The _properties_
            must have a _"default_path"_ or _"path"_ entry with the path of the CSV file:

            - _"default_path"_ `(str)`: The default path of the CSV file.\n
            - _"encoding"_ `(str)`: The encoding of the CSV file. The default value is `utf-8`.\n
            - _"default_data"_: The default data of the data nodes instantiated from this csv data node.\n
            - _"has_header"_ `(bool)`: If True, indicates that the CSV file has a header.\n
            - _"exposed_type"_: The exposed type of the data read from CSV file. The default value is `pandas`.\n
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
    ):
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

    def _read(self):
        if self.properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe()
        if self.properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy()
        return self._read_as()

    def _read_as(self):
        with open(self._path, encoding=self.properties[self.__ENCODING_KEY]) as csvFile:
            if self.properties[self._HAS_HEADER_PROPERTY]:
                reader = csv.DictReader(csvFile)
            else:
                reader = csv.reader(csvFile)

            return [self._decoder(line) for line in reader]

    def _read_as_numpy(self) -> np.ndarray:
        return self._read_as_pandas_dataframe().to_numpy()

    def _read_as_pandas_dataframe(
        self, usecols: Optional[List[int]] = None, column_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        try:
            if self.properties[self._HAS_HEADER_PROPERTY]:
                if column_names:
                    return pd.read_csv(self._path, encoding=self.properties[self.__ENCODING_KEY])[column_names]
                return pd.read_csv(self._path, encoding=self.properties[self.__ENCODING_KEY])
            else:
                if usecols:
                    return pd.read_csv(
                        self._path, encoding=self.properties[self.__ENCODING_KEY], header=None, usecols=usecols
                    )
                return pd.read_csv(self._path, encoding=self.properties[self.__ENCODING_KEY], header=None)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def _append(self, data: Any):
        if isinstance(data, pd.DataFrame):
            data.to_csv(self._path, mode="a", index=False, encoding=self.properties[self.__ENCODING_KEY], header=False)
        else:
            pd.DataFrame(data).to_csv(
                self._path, mode="a", index=False, encoding=self.properties[self.__ENCODING_KEY], header=False
            )

    def _write(self, data: Any):
        exposed_type = self.properties[self._EXPOSED_TYPE_PROPERTY]
        if self.properties[self._HAS_HEADER_PROPERTY]:
            self._convert_data_to_dataframe(exposed_type, data).to_csv(
                self._path, index=False, encoding=self.properties[self.__ENCODING_KEY]
            )
        else:
            self._convert_data_to_dataframe(exposed_type, data).to_csv(
                self._path, index=False, encoding=self.properties[self.__ENCODING_KEY], header=None
            )

    def write_with_column_names(self, data: Any, columns: Optional[List[str]] = None, job_id: Optional[JobId] = None):
        """Write a selection of columns.

        Parameters:
            data (Any): The data to write.
            columns (Optional[List[str]]): The list of column names to write.
            job_id (JobId^): An optional identifier of the writer.
        """
        df = self._convert_data_to_dataframe(self.properties[self._EXPOSED_TYPE_PROPERTY], data)
        if columns and isinstance(df, pd.DataFrame):
            df.columns = columns
        df.to_csv(self._path, index=False, encoding=self.properties[self.__ENCODING_KEY])
        self.track_edit(timestamp=datetime.now(), job_id=job_id)
