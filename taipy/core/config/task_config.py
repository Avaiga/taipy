from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.core.common._validate_id import _validate_id
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl
from taipy.core.config.data_node_config import DataNodeConfig


class TaskConfig:
    """
    Holds all the configuration fields needed to create actual tasks from the `TaskConfig`.

    Attributes:
        id (str): Identifier of the task config. Must be a valid Python variable name.
        inputs (list): List of `DataNodeConfig^` inputs. The default value is [].
        outputs (list): List of `DataNodeConfig^` outputs. The default value is [].
        function (Callable): User function taking as inputs some parameters compatible with the exposed types
            (exposed_type field) of the input data nodes and returning results compatible with the exposed types
            (exposed_type field) of the outputs list. The default value is None.
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    _INPUT_KEY = "inputs"
    _FUNCTION = "function"
    _OUTPUT_KEY = "outputs"

    def __init__(
        self,
        id: str,
        function,
        inputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        outputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        **properties,
    ):
        self.id = _validate_id(id)
        self.properties = properties
        if inputs:
            self._inputs = [inputs] if isinstance(inputs, DataNodeConfig) else copy(inputs)
        else:
            self._inputs = []
        if outputs:
            self._outputs = [outputs] if isinstance(outputs, DataNodeConfig) else copy(outputs)
        else:
            self._outputs = []
        self.function = function

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return TaskConfig(self.id, copy(self._inputs), self.function, copy(self._outputs), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return TaskConfig(id, None, [], [])

    def _to_dict(self):
        return {
            self._INPUT_KEY: self._inputs,
            self._FUNCTION: self.function,
            self._OUTPUT_KEY: self._outputs,
            **self.properties,
        }

    @classmethod
    def _from_dict(cls, id: str, config_as_dict: Dict[str, Any], dn_configs: Dict[str, DataNodeConfig]):
        funct = config_as_dict.pop(cls._FUNCTION, None)
        config = TaskConfig(id, funct)
        config.id = _validate_id(id)
        if inputs := config_as_dict.pop(cls._INPUT_KEY, None):
            config._inputs = [dn_configs[dn_id] for dn_id in inputs if dn_id in dn_configs]
        if outputs := config_as_dict.pop(cls._OUTPUT_KEY, None):
            config._outputs = [dn_configs[ds_id] for ds_id in outputs if ds_id in dn_configs]

        config.properties = config_as_dict
        return config

    @property
    def input_configs(self) -> List[DataNodeConfig]:
        return list(self._inputs)

    @property
    def output_configs(self) -> List[DataNodeConfig]:
        return list(self._outputs)

    def _update(self, config_as_dict, default_task_cfg=None):
        self._inputs = config_as_dict.pop(self._INPUT_KEY, self._inputs) or default_task_cfg._inputs
        self._outputs = config_as_dict.pop(self._OUTPUT_KEY, self._outputs) or default_task_cfg._outputs
        self.function = config_as_dict.pop(self._FUNCTION, self.function)
        self.properties.update(config_as_dict)
        if default_task_cfg:
            self.properties = {**default_task_cfg.properties, **self.properties}
        for k, v in self.properties.items():
            self.properties[k] = _tpl._replace_templates(v)
