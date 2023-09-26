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

import csv
import os
from datetime import datetime, timedelta
from os.path import isfile
from typing import Any, Dict, List, Optional, Set

import modin.pandas as modin_pd
import pandas as pd

from taipy.config.common.scope import Scope

from .._backup._backup import _replace_in_backup_file
from .._entity._reload import _self_reload
from .._version._version_manager_factory import _VersionManagerFactory
from ..job.job_id import JobId
from ._abstract_file import _AbstractFileDataNode
from ._abstract_tabular import _AbstractTabularDataNode
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class CSVDataNode(DataNode, _AbstractFileDataNode, _AbstractTabularDataNode):
    """Data Node stored as a CSV file.

    Attributes:
        config_id (str): Identifier of the data node configuration. This string must be a valid
            Python identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
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
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PANDAS = "pandas"
    __EXPOSED_TYPE_MODIN = "modin"
    __VALID_STRING_EXPOSED_TYPES = [__EXPOSED_TYPE_PANDAS, __EXPOSED_TYPE_MODIN, __EXPOSED_TYPE_NUMPY]
    __PATH_KEY = "path"
    __DEFAULT_PATH_KEY = "default_path"
    __ENCODING_KEY = "encoding"
    __DEFAULT_DATA_KEY = "default_data"
    __HAS_HEADER_PROPERTY = "has_header"
    _REQUIRED_PROPERTIES: List[str] = []

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
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
        if properties is None:
            properties = {}

        default_value = properties.pop(self.__DEFAULT_DATA_KEY, None)

        if self.__ENCODING_KEY not in properties.keys():
            properties[self.__ENCODING_KEY] = "utf-8"

        if self.__HAS_HEADER_PROPERTY not in properties.keys():
            properties[self.__HAS_HEADER_PROPERTY] = True

        if self.__EXPOSED_TYPE_PROPERTY not in properties.keys():
            properties[self.__EXPOSED_TYPE_PROPERTY] = self.__EXPOSED_TYPE_PANDAS
        self._check_exposed_type(properties[self.__EXPOSED_TYPE_PROPERTY], self.__VALID_STRING_EXPOSED_TYPES)

        super().__init__(
            config_id,
            scope,
            id,
            name,
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
        self._path = properties.get(self.__PATH_KEY, properties.get(self.__DEFAULT_PATH_KEY))
        if not self._path:
            self._path = self._build_path(self.storage_type())
        properties[self.__PATH_KEY] = self._path

        if not self._last_edit_date and isfile(self._path):
            self._last_edit_date = datetime.now()
        if default_value is not None and not os.path.exists(self._path):
            self.write(default_value)

        self._TAIPY_PROPERTIES.update(
            {
                self.__EXPOSED_TYPE_PROPERTY,
                self.__PATH_KEY,
                self.__DEFAULT_PATH_KEY,
                self.__ENCODING_KEY,
                self.__DEFAULT_DATA_KEY,
                self.__HAS_HEADER_PROPERTY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        tmp_old_path = self._path
        self._path = value
        self.properties[self.__PATH_KEY] = value
        _replace_in_backup_file(old_file_path=tmp_old_path, new_file_path=self._path)

    def _read(self):
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe()
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_MODIN:
            return self._read_as_modin_dataframe()
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy()
        return self._read_as()

    def _read_as(self):
        custom_class = self.properties[self.__EXPOSED_TYPE_PROPERTY]
        with open(self._path, encoding=self.properties[self.__ENCODING_KEY]) as csvFile:
            res = list()
            if self.properties[self.__HAS_HEADER_PROPERTY]:
                reader = csv.DictReader(csvFile)
                for line in reader:
                    res.append(custom_class(**line))
            else:
                reader = csv.reader(
                    csvFile,
                )
                for line in reader:
                    res.append(custom_class(*line))
            return res

    def _read_as_numpy(self):
        return self._read_as_pandas_dataframe().to_numpy()

    def _read_as_pandas_dataframe(
        self, usecols: Optional[List[int]] = None, column_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        try:
            if self.properties[self.__HAS_HEADER_PROPERTY]:
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

    def _read_as_modin_dataframe(
        self, usecols: Optional[List[int]] = None, column_names: Optional[List[str]] = None
    ) -> modin_pd.DataFrame:
        try:
            if self.properties[self.__HAS_HEADER_PROPERTY]:
                if column_names:
                    return modin_pd.read_csv(self._path, encoding=self.properties[self.__ENCODING_KEY])[column_names]
                return modin_pd.read_csv(self._path, encoding=self.properties[self.__ENCODING_KEY])
            else:
                if usecols:
                    return modin_pd.read_csv(
                        self._path, header=None, usecols=usecols, encoding=self.properties[self.__ENCODING_KEY]
                    )
                return modin_pd.read_csv(self._path, header=None, encoding=self.properties[self.__ENCODING_KEY])
        except pd.errors.EmptyDataError:
            return modin_pd.DataFrame()

    def _write(self, data: Any):
        if isinstance(data, (pd.DataFrame, modin_pd.DataFrame)):
            data.to_csv(self._path, index=False, encoding=self.properties[self.__ENCODING_KEY])
        else:
            pd.DataFrame(data).to_csv(self._path, index=False, encoding=self.properties[self.__ENCODING_KEY])

    def write_with_column_names(self, data: Any, columns: Optional[List[str]] = None, job_id: Optional[JobId] = None):
        """Write a selection of columns.

        Parameters:
            data (Any): The data to write.
            columns (Optional[List[str]]): The list of column names to write.
            job_id (JobId^): An optional identifier of the writer.
        """
        if not columns:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        df.to_csv(self._path, index=False, encoding=self.properties[self.__ENCODING_KEY])
        self.track_edit(timestamp=datetime.now(), job_id=job_id)
