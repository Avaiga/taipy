from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TaskModel:
    """
    Class to hold a model of a DataSource. A model refers to the structure of a
    Data Source stored in a database.

    Attributes
    ----------
    id: str
        identifier of a DataSource
    config_name: int
        name of the DataSourceConfig
    input: taipy.data.data_source.DataSource
        input data source of the Task, save as ID str
    function_name: str
        name of the task function
    function_module: str
        module name of the task function
    output: taipy.data.data_source.DataSource
        output data source of the Task, save as ID str

    Key
    ---
    The tuple config_name and parent_id formed a unique key
    """

    id: str
    config_name: str
    input_ids: List[str]
    function_name: str
    function_module: str
    output_ids: List[str]
