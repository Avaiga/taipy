import os
import pathlib
import pickle
from datetime import datetime
from typing import List, Optional

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.data.data_node import DataNode
from taipy.core.data.scope import Scope


class PickleDataNode(DataNode):
    """
    A Data Node stored as a pickle file.

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
        up_to_date (bool): `True` if the data is considered as up to date. `False` otherwise.
        properties (dict): Dict of additional arguments. Note that at the creation of the data node, if the property
            "default_data" is present, the data node is automatically written with the corresponding default_data value.
            If the property "path" is present, data will be stored using the corresponding value as the name of the
            file.
    """

    __STORAGE_TYPE = "pickle"
    __PICKLE_FILE_NAME = "path"
    __DEFAULT_DATA_VALUE = "default_data"
    REQUIRED_PROPERTIES: List[str] = []

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_days: Optional[int] = None,
        validity_hours: Optional[int] = None,
        validity_minutes: Optional[int] = None,
        edition_in_progress: bool = False,
        properties=None,
    ):
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
        super().__init__(
            config_name,
            scope,
            id,
            name,
            parent_id,
            last_edition_date,
            job_ids,
            validity_days,
            validity_hours,
            validity_minutes,
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
    def is_generated_file(self) -> bool:
        return self.__PICKLE_FILE_NAME not in self.properties

    def _read(self):
        return pickle.load(open(self.__pickle_file_path, "rb"))

    def _write(self, data):
        pickle.dump(data, open(self.__pickle_file_path, "wb"))

    def __build_path(self):
        if file_name := self._properties.get(self.__PICKLE_FILE_NAME):
            return file_name
        from taipy.core.config.config import Config

        dir_path = pathlib.Path(Config.global_config().storage_folder) / "pickles"
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{self.id}.p"
