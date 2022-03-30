from collections import defaultdict
from datetime import datetime, timedelta
from os.path import isfile
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from openpyxl import load_workbook

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.common.scope import Scope
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.exceptions import (
    MissingRequiredProperty,
    NonExistingExcelSheet,
    NotMatchSheetNameAndCustomObject,
)


class ExcelDataNode(DataNode):
    """
    A Data Node stored as an Excel file (xlsx format).

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python variable name.
        scope (`Scope^`): The `Scope^` of the data node.
        id (str): The unique identifier of the data node.
        name (str): A user-readable name of the data node.
        parent_id (str): The identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime): The date and time of the last edition.
        job_ids (List[str]): The ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): The validity period of a cacheable data node. Implemented as a
            timedelta. If _validity_period_ is set to None, the data_node is always up-to-date.
        edition_in_progress (bool): True if a task computing the data node has been submitted and not completed yet.
            False otherwise.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the _properties_ parameter must
            at least contain a "path" entry representing the path of the Excel file (xlsx format).
    """

    __STORAGE_TYPE = "excel"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __REQUIRED_PATH_PROPERTY = "path"
    __HAS_HEADER_PROPERTY = "has_header"
    __SHEET_NAME_PROPERTY = "sheet_name"
    _REQUIRED_PROPERTIES: List[str] = [__REQUIRED_PATH_PROPERTY]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_period: Optional[timedelta] = None,
        edition_in_progress: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}
        if missing := set(self._REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )
        if self.__SHEET_NAME_PROPERTY not in properties.keys():
            properties[self.__SHEET_NAME_PROPERTY] = None
        if self.__HAS_HEADER_PROPERTY not in properties.keys():
            properties[self.__HAS_HEADER_PROPERTY] = True
        if self.__EXPOSED_TYPE_PROPERTY in properties.keys():
            properties[self.__EXPOSED_TYPE_PROPERTY] = self.__exposed_types_to_dict(properties)

        super().__init__(
            config_id,
            scope,
            id,
            name,
            parent_id,
            last_edition_date,
            job_ids,
            validity_period,
            edition_in_progress,
            **properties,
        )
        if not self._last_edition_date and isfile(self._properties[self.__REQUIRED_PATH_PROPERTY]):
            self.unlock_edition()

    def __exposed_types_to_dict(self, properties):
        if properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
            return properties[self.__EXPOSED_TYPE_PROPERTY]
        if isinstance(properties[self.__EXPOSED_TYPE_PROPERTY], Dict):
            return properties[self.__EXPOSED_TYPE_PROPERTY]
        sheet_names = self.__sheet_name_to_list(properties)
        if isinstance(properties[self.__EXPOSED_TYPE_PROPERTY], List):
            if len(sheet_names) == len(properties[self.__EXPOSED_TYPE_PROPERTY]):
                return {
                    sheet_name: custom_obj
                    for sheet_name, custom_obj in zip(sheet_names, properties[self.__EXPOSED_TYPE_PROPERTY])
                }
            raise NotMatchSheetNameAndCustomObject
        return {sheet_name: properties[self.__EXPOSED_TYPE_PROPERTY] for sheet_name in sheet_names}

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if self.__EXPOSED_TYPE_PROPERTY in self.properties:
            if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
                return self._read_as_numpy()
            return self._read_as()
        return self._read_as_pandas_dataframe()

    def __sheet_name_to_list(self, properties):
        if properties[self.__SHEET_NAME_PROPERTY]:
            sheet_names = properties[self.__SHEET_NAME_PROPERTY]
        else:
            excel_file = load_workbook(properties[self.__REQUIRED_PATH_PROPERTY])
            sheet_names = excel_file.sheetnames
            excel_file.close()
        return sheet_names if isinstance(sheet_names, (List, Set, Tuple)) else [sheet_names]

    def _read_as(self):
        excel_file = load_workbook(self.properties[self.__REQUIRED_PATH_PROPERTY])
        custom_class_dict = self.properties[self.__EXPOSED_TYPE_PROPERTY]
        work_books = defaultdict()

        for sheet_name, custom_class in custom_class_dict.items():
            if not (sheet_name in excel_file.sheetnames):
                raise NonExistingExcelSheet(sheet_name, self.properties[self.__REQUIRED_PATH_PROPERTY])

            work_sheet = excel_file[sheet_name]
            res = list()
            for row in work_sheet.rows:
                res.append([col.value for col in row])
            if self.properties[self.__HAS_HEADER_PROPERTY]:
                header = res.pop(0)
                for i, row in enumerate(res):
                    res[i] = custom_class(**dict([[h, r] for h, r in zip(header, row)]))
            else:
                for i, row in enumerate(res):
                    res[i] = custom_class(*row)
            work_books[sheet_name] = res

        excel_file.close()

        if len(custom_class_dict) == 1:
            return work_books[list(custom_class_dict.keys())[0]]

        return work_books

    def _read_as_numpy(self):
        sheet_names = self.__sheet_name_to_list(self.properties)
        if len(sheet_names) > 1:
            return {sheet_name: df.to_numpy() for sheet_name, df in self._read_as_pandas_dataframe().items()}
        return self._read_as_pandas_dataframe().to_numpy()

    def _read_as_pandas_dataframe(self, usecols: Optional[List[int]] = None, column_names: Optional[List[str]] = None):
        try:
            if self.properties[self.__HAS_HEADER_PROPERTY]:
                if column_names:
                    return pd.read_excel(
                        self.properties[self.__REQUIRED_PATH_PROPERTY],
                        sheet_name=self.properties[self.__SHEET_NAME_PROPERTY],
                    )[column_names]
                return pd.read_excel(
                    self.properties[self.__REQUIRED_PATH_PROPERTY],
                    sheet_name=self.properties[self.__SHEET_NAME_PROPERTY],
                )
            else:
                if usecols:
                    return pd.read_excel(
                        self.properties[self.__REQUIRED_PATH_PROPERTY],
                        header=None,
                        usecols=usecols,
                        sheet_name=self.properties[self.__SHEET_NAME_PROPERTY],
                    )
                return pd.read_excel(
                    self.properties[self.__REQUIRED_PATH_PROPERTY],
                    header=None,
                    sheet_name=self.properties[self.__SHEET_NAME_PROPERTY],
                )
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def _write(self, data: Any):
        if isinstance(data, Dict) and all([isinstance(x, pd.DataFrame) for x in data.values()]):
            writer = pd.ExcelWriter(self.properties[self.__REQUIRED_PATH_PROPERTY])
            for key in data.keys():
                data[key].to_excel(writer, key, index=False)
            writer.save()
        else:
            pd.DataFrame(data).to_excel(self.properties[self.__REQUIRED_PATH_PROPERTY], index=False)

    def write_with_column_names(self, data: Any, columns: List[str] = None, job_id: Optional[JobId] = None):
        """
        Write only the columns provided in _columns_ parameter.

        Parameters:
            data (Any): The data to write.
            columns (List[str]): The list of columns to write.
            job_id (`JobId^`): An optional identifier of the writer.
        """
        if not columns:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        df.to_excel(self.path, index=False)
        self._last_edition_date = datetime.now()
        if job_id:
            self.job_ids.append(job_id)
