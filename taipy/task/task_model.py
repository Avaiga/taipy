from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TaskModel:
    """
    Hold the model of a Task.
    
    A model refers to the structure of a Task stored in a database.

    Attributes:
        id (str): Identifier of a Data Source.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        config_name (int): Name of the Data Source Config.
        input (taipy.data.data_source.DataSource): Input data source of the Task, saved as its ID string representation.
        function_name (str): Name of the task function.
        function_module (str): Module name of the task function.
        output (taipy.data.data_source.DataSource): Output data source of the Task, saved as its ID string representation.

    Note:
        The tuple `(config_name, parent_id)` forms a unique key.
    """

    id: str
    parent_id: Optional[str]
    config_name: str
    input_ids: List[str]
    function_name: str
    function_module: str
    output_ids: List[str]
