import os
import pathlib
import pickle
from datetime import datetime, timedelta
from typing import List, Optional

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.common.scope import Scope
from taipy.core.data.data_node import DataNode


class PickleDataNode(DataNode):
    """
    A Data Node stored as a pickle file.

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
        properties (dict[str, Any]): A dictionary of additional properties.
            At creation of an _InMemory_ data node, if the _properties_ dictionary contains a "default_data" entry,
            the data node is automatically written with the corresponding "default_data" value.
            If the _properties_ dictionary contains a "path" entry, the data will be stored using the corresponding
            value as the name of the pickle file.
    """

    __STORAGE_TYPE = "pickle"
    __PICKLE_FILE_NAME = "path"
    __DEFAULT_DATA_VALUE = "default_data"
    _REQUIRED_PROPERTIES: List[str] = []

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
        properties=None,
    ):
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
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
        self.__pickle_file_path = self.__build_path()
        if not self._last_edition_date and os.path.exists(self.__pickle_file_path):
            self.unlock_edition()
        if default_value is not None and not os.path.exists(self.__pickle_file_path):
            self.write(default_value)

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property
    def path(self) -> str:
        return self.__pickle_file_path

    @property
    def is_file_generated(self) -> bool:
        return self.__PICKLE_FILE_NAME not in self.properties

    def _read(self):
        return pickle.load(open(self.__pickle_file_path, "rb"))

    def _write(self, data):
        pickle.dump(data, open(self.__pickle_file_path, "wb"))

    def __build_path(self):
        if file_name := self._properties.get(self.__PICKLE_FILE_NAME):
            return file_name
        from taipy.core.config.config import Config

        dir_path = pathlib.Path(Config.global_config.storage_folder) / "pickles"
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{self.id}.p"
