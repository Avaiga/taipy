from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.core.common._unicode_to_python_variable_name import _protect_name
from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl
from taipy.core.config.data_node_config import DataNodeConfig


class TaskConfig:
    """
    Holds all the configuration fields needed to create actual tasks from the TaskConfig.

    Attributes:
        id (str): Identifier of the task config.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        inputs (list): List of data node config inputs. Default value: [].
        outputs (list): List of data node config outputs. Default value: [].
        function (Callable): User function taking as inputs some parameters compatible with the exposed types
            (exposed_type field) of the inputs data nodes and returning results compatible with the exposed types
            (exposed_type field) of the outputs list. Default value: None.
        properties (dict): Dictionary of additional properties.
    """

    INPUT_KEY = "inputs"
    FUNCTION = "function"
    OUTPUT_KEY = "outputs"

    def __init__(
        self,
        id: str,
        function,
        inputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        outputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        **properties,
    ):
        self.id = _protect_name(id)
        self.properties = properties
        if inputs:
            self.inputs = [inputs] if isinstance(inputs, DataNodeConfig) else copy(inputs)
        else:
            self.inputs = []
        if outputs:
            self.outputs = [outputs] if isinstance(outputs, DataNodeConfig) else copy(outputs)
        else:
            self.outputs = []
        self.function = function

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return TaskConfig(self.id, copy(self.inputs), self.function, copy(self.outputs), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return TaskConfig(id, None, [], [])

    def to_dict(self):
        return {
            self.INPUT_KEY: self.inputs,
            self.FUNCTION: self.function,
            self.OUTPUT_KEY: self.outputs,
            **self.properties,
        }

    @classmethod
    def from_dict(cls, id: str, config_as_dict: Dict[str, Any], dn_configs: Dict[str, DataNodeConfig]):
        funct = config_as_dict.pop(cls.FUNCTION, None)
        config = TaskConfig(id, funct)
        config.id = _protect_name(id)
        if inputs := config_as_dict.pop(cls.INPUT_KEY, None):
            config.inputs = [dn_configs[dn_id] for dn_id in inputs if dn_id in dn_configs]
        if outputs := config_as_dict.pop(cls.OUTPUT_KEY, None):
            config.outputs = [dn_configs[ds_id] for ds_id in outputs if ds_id in dn_configs]

        config.properties = config_as_dict
        return config

    @property
    def input(self) -> List[DataNodeConfig]:
        return list(self.inputs)

    @property
    def output(self) -> List[DataNodeConfig]:
        return list(self.outputs)

    def update(self, config_as_dict, default_task_cfg=None):
        self.inputs = config_as_dict.pop(self.INPUT_KEY, self.inputs) or default_task_cfg.inputs
        self.outputs = config_as_dict.pop(self.OUTPUT_KEY, self.outputs) or default_task_cfg.outputs
        self.function = config_as_dict.pop(self.FUNCTION, self.function)
        self.properties.update(config_as_dict)
        if default_task_cfg:
            self.properties = {**default_task_cfg.properties, **self.properties}
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)
