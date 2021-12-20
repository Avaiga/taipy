from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.common import protect_name
from taipy.config import DataSourceConfig


class TaskConfig:
    """
    Holds all the configuration fields needed to create actual tasks from the TaskConfig.

    Attributes:
        name (str):  Unique name as an identifier of the task config.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        inputs (list): List of data source config inputs. Default value: [].
        outputs (list): List of data source config outputs. Default value: [].
        function (Callable): User function taking as inputs some parameters compatible with the exposed types
            (exposed_type field) of the inputs data sources and returning results compatible with the exposed types
            (exposed_type field) of the outputs list. Default value: None.
        properties (dict): Dictionary of additional properties.
    """

    INPUT_KEY = "inputs"
    FUNCTION = "function"
    OUTPUT_KEY = "outputs"

    def __init__(
        self,
        name: str = None,
        inputs: Union[DataSourceConfig, List[DataSourceConfig]] = None,
        function=None,
        outputs: Union[DataSourceConfig, List[DataSourceConfig]] = None,
        **properties,
    ):
        self.name = protect_name(name) if name else name
        self.properties = properties
        if inputs:
            self.inputs = [inputs] if isinstance(inputs, DataSourceConfig) else copy(inputs)
        else:
            self.inputs = []
        if outputs:
            self.outputs = [outputs] if isinstance(outputs, DataSourceConfig) else copy(outputs)
        else:
            self.outputs = []
        self.function = function

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return TaskConfig(self.name, copy(self.inputs), self.function, copy(self.outputs), **copy(self.properties))

    @classmethod
    def default_config(cls, name):
        return TaskConfig(name, [], None, [])

    def to_dict(self):
        return {
            self.INPUT_KEY: self.inputs,
            self.FUNCTION: self.function,
            self.OUTPUT_KEY: self.outputs,
            **self.properties,
        }

    @classmethod
    def from_dict(cls, name: str, config_as_dict: Dict[str, Any], ds_configs: Dict[str, DataSourceConfig]):
        config = TaskConfig(name)
        config.name = protect_name(name)
        if inputs := config_as_dict.pop(cls.INPUT_KEY, None):
            config.inputs = [ds_configs[ds_id] for ds_id in inputs if ds_id in ds_configs]
        if outputs := config_as_dict.pop(cls.OUTPUT_KEY, None):
            config.outputs = [ds_configs[ds_id] for ds_id in outputs if ds_id in ds_configs]
        if funct := config_as_dict.pop(cls.OUTPUT_KEY, None):
            config.function = funct
        config.properties = config_as_dict
        return config

    @property
    def input(self) -> List[DataSourceConfig]:
        return list(self.inputs)

    @property
    def output(self) -> List[DataSourceConfig]:
        return list(self.outputs)

    def update(self, config_as_dict, default_task_cfg=None):
        self.inputs = config_as_dict.pop(self.INPUT_KEY, self.inputs) or default_task_cfg.inputs
        self.outputs = config_as_dict.pop(self.OUTPUT_KEY, self.outputs) or default_task_cfg.outputs
        self.function = config_as_dict.pop(self.FUNCTION, self.function)
        self.properties.update(config_as_dict)
        if default_task_cfg:
            self.properties = {**default_task_cfg.properties, **self.properties}
