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

import os
from datetime import datetime, timedelta
from os.path import isdir, isfile
from typing import Any, Dict, List, Optional, Set

import modin.pandas as modin_pd
import pandas as pd

from taipy.config.common.scope import Scope

from .._backup._backup import _replace_in_backup_file
from .._entity._reload import _self_reload
from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import UnknownCompressionAlgorithm, UnknownParquetEngine
from ..job.job_id import JobId
from ._abstract_file import _AbstractFileDataNode
from ._abstract_tabular import _AbstractTabularDataNode
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class ParquetDataNode(DataNode, _AbstractFileDataNode, _AbstractTabularDataNode):
    """Data Node stored as a Parquet file.

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
        path (str): The path to the Parquet file.
        properties (dict[str, Any]): A dictionary of additional properties. *properties*
            must have a *"default_path"* or *"path"* entry with the path of the Parquet file:

            - *"default_path"* (`str`): The default path of the Parquet file.
            - *"exposed_type"*: The exposed type of the data read from Parquet file. The default
                value is `pandas`.
            - *"engine"* (`Optional[str]`): Parquet library to use. Possible values are
                *"fastparquet"* or *"pyarrow"*.<br/>
                The default value is *"pyarrow"*.
            - *"compression"* (`Optional[str]`): Name of the compression to use. Possible values
                are *"snappy"*, *"gzip"*, *"brotli"*, or *"none"* (no compression).<br/>
                The default value is *"snappy"*.
            - *"read_kwargs"* (`Optional[dict]`): Additional parameters passed to the
                *pandas.read_parquet()* function.
            - *"write_kwargs"* (`Optional[dict]`): Additional parameters passed to the
                *pandas.DataFrame.write_parquet()* fucntion.
                The parameters in *"read_kwargs"* and *"write_kwargs"* have a
                **higher precedence** than the top-level parameters which are also passed to
                Pandas.
    """

    __STORAGE_TYPE = "parquet"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PANDAS = "pandas"
    __EXPOSED_TYPE_MODIN = "modin"
    __VALID_STRING_EXPOSED_TYPES = [__EXPOSED_TYPE_PANDAS, __EXPOSED_TYPE_MODIN, __EXPOSED_TYPE_NUMPY]
    __PATH_KEY = "path"
    __DEFAULT_DATA_KEY = "default_data"
    __DEFAULT_PATH_KEY = "default_path"
    __ENGINE_PROPERTY = "engine"
    __VALID_PARQUET_ENGINES = ["pyarrow", "fastparquet"]
    __COMPRESSION_PROPERTY = "compression"
    __VALID_COMPRESSION_ALGORITHMS = ["snappy", "gzip", "brotli", "none"]
    __READ_KWARGS_PROPERTY = "read_kwargs"
    __WRITE_KWARGS_PROPERTY = "write_kwargs"
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

        if self.__ENGINE_PROPERTY not in properties.keys():
            properties[self.__ENGINE_PROPERTY] = "pyarrow"
        if properties[self.__ENGINE_PROPERTY] not in self.__VALID_PARQUET_ENGINES:
            raise UnknownParquetEngine(
                f"Invalid parquet engine: {properties[self.__ENGINE_PROPERTY]}. "
                f"Supported engines are {', '.join(self.__VALID_PARQUET_ENGINES)}"
            )

        if self.__COMPRESSION_PROPERTY not in properties.keys():
            properties[self.__COMPRESSION_PROPERTY] = "snappy"
        if properties[self.__COMPRESSION_PROPERTY] == "none":
            properties[self.__COMPRESSION_PROPERTY] = None
        if (
            properties[self.__COMPRESSION_PROPERTY]
            and properties[self.__COMPRESSION_PROPERTY] not in self.__VALID_COMPRESSION_ALGORITHMS
        ):
            raise UnknownCompressionAlgorithm(
                f"Unsupported compression algorithm: {properties[self.__COMPRESSION_PROPERTY]}. "
                f"Supported algorithms are {', '.join(self.__VALID_COMPRESSION_ALGORITHMS)}"
            )

        if self.__READ_KWARGS_PROPERTY not in properties.keys():
            properties[self.__READ_KWARGS_PROPERTY] = {}

        if self.__WRITE_KWARGS_PROPERTY not in properties.keys():
            properties[self.__WRITE_KWARGS_PROPERTY] = {}

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

        if default_value is not None and not os.path.exists(self._path):
            self.write(default_value)

        if not self._last_edit_date and (isfile(self._path) or isdir(self._path)):
            self._last_edit_date = datetime.now()

        self._TAIPY_PROPERTIES.update(
            {
                self.__EXPOSED_TYPE_PROPERTY,
                self.__PATH_KEY,
                self.__DEFAULT_PATH_KEY,
                self.__DEFAULT_DATA_KEY,
                self.__ENGINE_PROPERTY,
                self.__COMPRESSION_PROPERTY,
                self.__READ_KWARGS_PROPERTY,
                self.__WRITE_KWARGS_PROPERTY,
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
        return self.read_with_kwargs()

    def _read_as(self, read_kwargs: Dict):
        custom_class = self.properties[self.__EXPOSED_TYPE_PROPERTY]
        list_of_dicts = self._read_as_pandas_dataframe(read_kwargs).to_dict(orient="records")
        return [custom_class(**dct) for dct in list_of_dicts]

    def _read_as_numpy(self, read_kwargs: Dict):
        return self._read_as_pandas_dataframe(read_kwargs).to_numpy()

    def _read_as_pandas_dataframe(self, read_kwargs: Dict) -> pd.DataFrame:
        return pd.read_parquet(self._path, **read_kwargs)

    def _read_as_modin_dataframe(self, read_kwargs: Dict) -> modin_pd.DataFrame:
        return modin_pd.read_parquet(self._path, **read_kwargs)

    def _write(self, data: Any):
        self.write_with_kwargs(data)

    def write_with_kwargs(self, data: Any, job_id: Optional[JobId] = None, **write_kwargs):
        """Write the data referenced by this data node.

        Keyword arguments here which are also present in the Data Node config will overwrite them.

        Parameters:
            data (Any): The data to write.
            job_id (JobId^): An optional identifier of the writer.
            **write_kwargs (dict[str, any]): The keyword arguments passed to the function
                `pandas.DataFrame.to_parquet()`.
        """
        kwargs = {
            self.__ENGINE_PROPERTY: self.properties[self.__ENGINE_PROPERTY],
            self.__COMPRESSION_PROPERTY: self.properties[self.__COMPRESSION_PROPERTY],
        }
        kwargs.update(self.properties[self.__WRITE_KWARGS_PROPERTY])
        kwargs.update(write_kwargs)
        if isinstance(data, (pd.DataFrame, modin_pd.DataFrame)):
            data.to_parquet(self._path, **kwargs)
        else:
            pd.DataFrame(data).to_parquet(self._path, **kwargs)
        self.track_edit(timestamp=datetime.now(), job_id=job_id)

    def read_with_kwargs(self, **read_kwargs):
        """Read data from this data node.

        Keyword arguments here which are also present in the Data Node config will overwrite them.

        Parameters:
            **read_kwargs (dict[str, any]): The keyword arguments passed to the function
                `pandas.read_parquet()`.
        """
        # return None if data was never written
        if not self.last_edit_date:
            self._DataNode__logger.warning(
                f"Data node {self.id} from config {self.config_id} is being read but has never been written."
            )
            return None

        kwargs = self.properties[self.__READ_KWARGS_PROPERTY]
        kwargs.update(
            {
                self.__ENGINE_PROPERTY: self.properties[self.__ENGINE_PROPERTY],
            }
        )
        kwargs.update(read_kwargs)

        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe(kwargs)
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_MODIN:
            return self._read_as_modin_dataframe(kwargs)
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy(kwargs)
        return self._read_as(kwargs)
