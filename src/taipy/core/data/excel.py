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

from collections import defaultdict
from datetime import datetime, timedelta
from os.path import isfile
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
from openpyxl import load_workbook

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..common._reload import _self_reload
from ..common.alias import DataNodeId, Edit, JobId
from ..exceptions.exceptions import (
    ExposedTypeLengthMismatch,
    InvalidExposedType,
    MissingRequiredProperty,
    NonExistingExcelSheet,
)
from .data_node import DataNode


class ExcelDataNode(DataNode):
    """Data Node stored as an Excel file.

    The Excel file format is _xlsx_.

    Attributes:
        config_id (str): Identifier of this data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (pipeline_id, scenario_id, cycle_id) or
            `None`.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The validity period of a data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        path (str): The path to the Excel file.
        properties (dict[str, Any]): A dictionary of additional properties. The _properties_
            must have a _"default_path"_ or _"path"_ entry with the path of the Excel file:

            - _"default_path"_ `(str)`: The path of the Excel file.\n
            - _"has_header"_ `(bool)`: If True, indicates that the Excel file has a header.\n
            - _"sheet_name"_ `(Union[List[str], str])`: The list of sheet names to be used. This
                can be a unique name.\n
            - _"exposed_type"_: The exposed type of the data read from Excel file. The default value is `pandas`.\n
    """

    __STORAGE_TYPE = "excel"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PANDAS = "pandas"
    __EXPOSED_TYPE_MODIN = "modin"
    __VALID_STRING_EXPOSED_TYPES = [__EXPOSED_TYPE_PANDAS, __EXPOSED_TYPE_MODIN, __EXPOSED_TYPE_NUMPY]
    __PATH_KEY = "path"
    __DEFAULT_PATH_KEY = "default_path"
    __HAS_HEADER_PROPERTY = "has_header"
    __SHEET_NAME_PROPERTY = "sheet_name"
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

        self._path = properties.get(self.__PATH_KEY, properties.get(self.__DEFAULT_PATH_KEY))
        if self._path is None:
            raise MissingRequiredProperty("default_path is required in a Excel data node config")
        else:
            properties[self.__PATH_KEY] = self._path

        if self.__SHEET_NAME_PROPERTY not in properties.keys():
            properties[self.__SHEET_NAME_PROPERTY] = None
        if self.__HAS_HEADER_PROPERTY not in properties.keys():
            properties[self.__HAS_HEADER_PROPERTY] = True
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

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.properties[self.__PATH_KEY] = value

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _check_exposed_type(self, exposed_type):
        if isinstance(exposed_type, str) and exposed_type not in self.__VALID_STRING_EXPOSED_TYPES:
            raise InvalidExposedType(
                f"Invalid string exposed type {exposed_type}. Supported values are "
                f"{', '.join(self.__VALID_STRING_EXPOSED_TYPES)}"
            )
        elif isinstance(exposed_type, list):
            for t in exposed_type:
                self._check_exposed_type(t)
        elif isinstance(exposed_type, dict):
            for t in exposed_type.values():
                self._check_exposed_type(t)

    def _read(self):
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe()
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_MODIN:
            return self._read_as_modin_dataframe()
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy()
        return self._read_as()

    def __sheet_name_to_list(self, properties):
        if properties[self.__SHEET_NAME_PROPERTY]:
            sheet_names = properties[self.__SHEET_NAME_PROPERTY]
        else:
            excel_file = load_workbook(properties[self.__PATH_KEY])
            sheet_names = excel_file.sheetnames
            excel_file.close()
        return sheet_names if isinstance(sheet_names, (List, Set, Tuple)) else [sheet_names]

    def _read_as(self):
        excel_file = load_workbook(self._path)
        exposed_type = self.properties[self.__EXPOSED_TYPE_PROPERTY]
        work_books = defaultdict()
        sheet_names = excel_file.sheetnames
        provided_sheet_names = self.__sheet_name_to_list(self.properties)

        for sheet_name in provided_sheet_names:
            if sheet_name not in sheet_names:
                raise NonExistingExcelSheet(sheet_name, self._path)

        if isinstance(exposed_type, List):
            if len(provided_sheet_names) != len(self.properties[self.__EXPOSED_TYPE_PROPERTY]):
                raise ExposedTypeLengthMismatch(
                    f"Expected {len(provided_sheet_names)} exposed types, got "
                    f"{len(self.properties[self.__EXPOSED_TYPE_PROPERTY])}"
                )

        for i, sheet_name in enumerate(provided_sheet_names):
            work_sheet = excel_file[sheet_name]
            sheet_exposed_type = exposed_type

            if not isinstance(sheet_exposed_type, str):
                if isinstance(exposed_type, dict):
                    sheet_exposed_type = exposed_type.get(sheet_name, self.__EXPOSED_TYPE_PANDAS)
                elif isinstance(exposed_type, List):
                    sheet_exposed_type = exposed_type[i]

                if isinstance(sheet_exposed_type, str):
                    if sheet_exposed_type == self.__EXPOSED_TYPE_NUMPY:
                        work_books[sheet_name] = self._read_as_pandas_dataframe(sheet_name).to_numpy()
                    elif sheet_exposed_type == self.__EXPOSED_TYPE_PANDAS:
                        work_books[sheet_name] = self._read_as_pandas_dataframe(sheet_name)
                    continue

            res = list()
            for row in work_sheet.rows:
                res.append([col.value for col in row])
            if self.properties[self.__HAS_HEADER_PROPERTY] and res:
                header = res.pop(0)
                for i, row in enumerate(res):
                    res[i] = sheet_exposed_type(**dict([[h, r] for h, r in zip(header, row)]))
            else:
                for i, row in enumerate(res):
                    res[i] = sheet_exposed_type(*row)
            work_books[sheet_name] = res

        excel_file.close()

        if len(provided_sheet_names) == 1:
            return work_books[provided_sheet_names[0]]
        return work_books

    def _read_as_numpy(self):
        sheets = self._read_as_pandas_dataframe()
        if isinstance(sheets, dict):
            return {sheet_name: df.to_numpy() for sheet_name, df in sheets.items()}
        return sheets.to_numpy()

    def _read_as_pandas_dataframe(self, sheet_names=None) -> Union[Dict[Union[int, str], pd.DataFrame], pd.DataFrame]:
        if sheet_names is None:
            sheet_names = self.properties[self.__SHEET_NAME_PROPERTY]
        try:
            kwargs: Dict[str, Any] = {}
            if not self.properties[self.__HAS_HEADER_PROPERTY]:
                kwargs["header"] = None
            df = pd.read_excel(
                self._path,
                sheet_name=sheet_names,
                **kwargs,
            )
            if isinstance(df, dict):
                for key, value in df.items():
                    df[key] = pd.DataFrame(value)
                return df

            return pd.DataFrame(df)

        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def _read_as_modin_dataframe(
        self, sheet_names=None
    ) -> Union[Dict[Union[int, str], modin_pd.DataFrame], modin_pd.DataFrame]:
        if sheet_names is None:
            sheet_names = self.properties[self.__SHEET_NAME_PROPERTY]
        try:
            kwargs: Dict[str, Any] = {}
            if not self.properties[self.__HAS_HEADER_PROPERTY]:
                kwargs["header"] = None
            if kwargs.get("header", None):
                return modin_pd.read_excel(
                    self._path,
                    sheet_name=sheet_names,
                    **kwargs,
                )
            else:
                df = pd.read_excel(
                    self._path,
                    sheet_name=sheet_names,
                    **kwargs,
                )
                if isinstance(df, dict):
                    for key, value in df.items():
                        df[key] = modin_pd.DataFrame(value)
                    return df

            return modin_pd.DataFrame(df)

        except pd.errors.EmptyDataError:
            return modin_pd.DataFrame()

    def _write(self, data: Any):
        if isinstance(data, Dict) and all(
            [isinstance(x, (pd.DataFrame, modin_pd.DataFrame, np.ndarray)) for x in data.values()]
        ):
            with pd.ExcelWriter(self._path) as writer:
                for key in data.keys():
                    if isinstance(data[key], np.ndarray):
                        pd.DataFrame(data[key]).to_excel(writer, key, index=False)
                    else:
                        data[key].to_excel(writer, key, index=False)
        elif isinstance(data, (pd.DataFrame, modin_pd.DataFrame)):
            data.to_excel(self._path, index=False)
        else:
            pd.DataFrame(data).to_excel(self._path, index=False)

    def write_with_column_names(self, data: Any, columns: List[str] = None, job_id: Optional[JobId] = None):
        """Write a set of columns.

        Parameters:
            data (Any): The data to write.
            columns (List[str]): The list of column names to write.
            job_id (JobId^): An optional identifier of the writer.
        """
        if not columns:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        df.to_excel(self.path, index=False)
        self._track_edit(timestamp=datetime.now(), job_id=job_id)
