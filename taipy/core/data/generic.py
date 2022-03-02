from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.data.data_node import DataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.data_node import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction


class GenericDataNode(DataNode):
    """
    A generic Data Node that accepts custom read function and custom write function.

    Attributes:
        config_name (str):  Name that identifies the data node.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        scope (Scope):  The usage scope of this data node.
        id (str): Unique identifier of this data node.
        name (str): User-readable name of the data node.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime):  Date and time of the last edition.
        job_ids (List[str]): Ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): Number of weeks, days, hours, minutes, and seconds as a
            timedelta object to represent the data node validity duration. If validity_period is set to None,
            the data_node is always up to date.
        properties (dict): Dict of additional arguments. Note that the properties parameter should at least contain
            a value for "read_fct" and "write_fct" properties.
    """

    __STORAGE_TYPE = "generic"
    _REQUIRED_READ_FUNCTION_PROPERTY = "read_fct"
    __READ_FUNCTION_PARAMS_PROPERTY = "read_fct_params"
    _REQUIRED_WRITE_FUNCTION_PROPERTY = "write_fct"
    __WRITE_FUNCTION_PARAMS_PROPERTY = "write_fct_params"
    REQUIRED_PROPERTIES: List[str] = [_REQUIRED_READ_FUNCTION_PROPERTY, _REQUIRED_WRITE_FUNCTION_PROPERTY]

    def __init__(
        self,
        config_name: str,
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
        if missing := set(self.REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

        super().__init__(
            config_name,
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
        if not self._last_edition_date:
            self.unlock_edition()

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if read_fct := self.properties[self._REQUIRED_READ_FUNCTION_PROPERTY]:
            if self.__READ_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                return read_fct(**self.properties[self.__READ_FUNCTION_PARAMS_PROPERTY])
            return read_fct()
        raise MissingReadFunction

    def _write(self, data: Any):
        if write_fct := self.properties[self._REQUIRED_WRITE_FUNCTION_PROPERTY]:
            if self.__WRITE_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                return write_fct(data, **self.properties[self.__WRITE_FUNCTION_PARAMS_PROPERTY])
            return write_fct(data)
        raise MissingWriteFunction
