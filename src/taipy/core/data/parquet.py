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

from datetime import datetime, timedelta
from os.path import isfile
from typing import Any, Dict, List, Optional, Set

import modin.pandas as modin_pd
import pandas as pd

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..common._reload import _self_reload
from ..common.alias import DataNodeId, Edit, JobId
from ..exceptions.exceptions import (
    InvalidExposedType,
    MissingRequiredProperty,
    UnknownCompressionAlgorithm,
    UnknownParquetEngine,
)
from .data_node import DataNode


class ParquetDataNode(DataNode):
    """Data Node stored as a Parquet file.

    Attributes:
        config_id (str): Identifier of the data node configuration. This string must be a valid
            Python identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (pipeline_id, scenario_id, cycle_id) or `None`.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The validity period of a data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data_node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        path (str): The path to the Parquet file.
        properties (dict[str, Any]): A dictionary of additional properties. The _properties_
            must have a _"default_path"_ or _"path"_ entry with the path of the Parquet file:

            - _"default_path"_ `(str)`: The default path of the Parquet file.\n
            - _"exposed_type"_: The exposed type of the data read from Parquet file. The default value is `pandas`.\n
            - _"engine"_ `(Optional[str])`: Parquet library to use. Possible values are _"fastparquet"_ or _"pyarrow"_.
                The default value is _"pyarrow"_.
            - _"compression"_ `(Optional[str])`: Name of the compression to use. Use None for no compression.
                `{'snappy', 'gzip', 'brotli', None}`, default `'snappy'`.\n
            - _"read_kwargs"_ `(Optional[Dict])`: Additional parameters passed to the _pandas.read_parquet_ method.\n
            - _"write_kwargs"_ `(Optional[Dict])`: Additional parameters passed to the _pandas.DataFrame.write_parquet_
                method.
                The parameters in _"read_kwargs"_ and _"write_kwargs"_ have a **higher precedence** than the top-level
                parameters which are also passed to Pandas.\n
    """

    __STORAGE_TYPE = "parquet"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PANDAS = "pandas"
    __EXPOSED_TYPE_MODIN = "modin"
    __VALID_STRING_EXPOSED_TYPES = [__EXPOSED_TYPE_PANDAS, __EXPOSED_TYPE_MODIN, __EXPOSED_TYPE_NUMPY]
    __PATH_KEY = "path"
    __DEFAULT_PATH_KEY = "default_path"
    __ENGINE_PROPERTY = "engine"
    __VALID_PARQUET_ENGINES = ["pyarrow", "fastparquet"]
    __COMPRESSION_PROPERTY = "compression"
    __VALID_COMPRESSION_ALGORITHMS = ["snappy", "gzip", "brotli"]
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
        edits: List[Edit] = None,
        version: str = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}
        if missing := set(self._REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

        if self.__ENGINE_PROPERTY not in properties.keys():
            properties[self.__ENGINE_PROPERTY] = "pyarrow"
        if properties[self.__ENGINE_PROPERTY] not in self.__VALID_PARQUET_ENGINES:
            raise UnknownParquetEngine(
                f"Invalid parquet engine: {properties[self.__ENGINE_PROPERTY]}. "
                f"Supported engines are {', '.join(self.__VALID_PARQUET_ENGINES)}"
            )

        if self.__COMPRESSION_PROPERTY not in properties.keys():
            properties[self.__COMPRESSION_PROPERTY] = "snappy"
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

        self._path = properties.get(self.__PATH_KEY, properties.get(self.__DEFAULT_PATH_KEY))
        if self._path is None:
            raise MissingRequiredProperty("default_path is required in a Parquet data node config")
        else:
            properties[self.__PATH_KEY] = self._path

        if self.__EXPOSED_TYPE_PROPERTY not in properties.keys():
            properties[self.__EXPOSED_TYPE_PROPERTY] = self.__EXPOSED_TYPE_PANDAS
        self._check_exposed_type(properties[self.__EXPOSED_TYPE_PROPERTY])

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
            **properties,
        )
        if not self._last_edit_date and isfile(self._path):
            self.last_edit_date = datetime.now()  # type: ignore

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.properties[self.__PATH_KEY] = value

    def _check_exposed_type(self, exposed_type):
        if isinstance(exposed_type, str) and exposed_type not in self.__VALID_STRING_EXPOSED_TYPES:
            raise InvalidExposedType(
                f"Invalid string exposed type {exposed_type}. Supported values are "
                f"{', '.join(self.__VALID_STRING_EXPOSED_TYPES)}"
            )

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
        """Write data, with keyword arguments passed to `pandas.DataFrame.to_parquet`.

        Keyword arguments here which are also present in the Data Node config will overwrite them.

        Parameters:
            data (Any): The data to write.
            job_id (JobId^): An optional identifier of the writer.
            **write_kwargs: The keyword arguments are passed to `pandas.DataFrame.to_parquet`.
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
        self._track_edit(timestamp=datetime.now(), job_id=job_id)

    def read_with_kwargs(self, **read_kwargs):
        """Read data node, with keyword arguments passed to `pandas.read_parquet`.

        Keyword arguments here which are also present in the Data Node config will overwrite them.

        Parameters:
            **read_kwargs: The keyword arguments are passed to `pandas.read_parquet`.
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
