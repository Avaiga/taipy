from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.data.data_node import DataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction


class GenericDataNode(DataNode):
    """
    A generic Data Node that accepts custom read python function and custom write python function.

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
            at least contain an entry for "read_fct" or "write_fct" representing the read and write functions.
    """

    __STORAGE_TYPE = "generic"
    _REQUIRED_READ_FUNCTION_PROPERTY = "read_fct"
    __READ_FUNCTION_PARAMS_PROPERTY = "read_fct_params"
    _REQUIRED_WRITE_FUNCTION_PROPERTY = "write_fct"
    __WRITE_FUNCTION_PARAMS_PROPERTY = "write_fct_params"
    _REQUIRED_PROPERTIES: List[str] = [_REQUIRED_READ_FUNCTION_PROPERTY, _REQUIRED_WRITE_FUNCTION_PROPERTY]

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
        if not self._last_edition_date:
            self.unlock_edition()

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if read_fct := self.properties[self._REQUIRED_READ_FUNCTION_PROPERTY]:
            if self.__READ_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                if isinstance(self.properties[self.__READ_FUNCTION_PARAMS_PROPERTY], Dict):
                    return read_fct(**self.properties[self.__READ_FUNCTION_PARAMS_PROPERTY])
                if isinstance(self.properties[self.__READ_FUNCTION_PARAMS_PROPERTY], List):
                    return read_fct(*self.properties[self.__READ_FUNCTION_PARAMS_PROPERTY])
            return read_fct()
        raise MissingReadFunction

    def _write(self, data: Any):
        if write_fct := self.properties[self._REQUIRED_WRITE_FUNCTION_PROPERTY]:
            if self.__WRITE_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                if isinstance(self.properties[self.__WRITE_FUNCTION_PARAMS_PROPERTY], Dict):
                    return write_fct(data, **self.properties[self.__WRITE_FUNCTION_PARAMS_PROPERTY])
                if isinstance(self.properties[self.__WRITE_FUNCTION_PARAMS_PROPERTY], List):
                    return write_fct(data, *self.properties[self.__WRITE_FUNCTION_PARAMS_PROPERTY])
            return write_fct(data)
        raise MissingWriteFunction
