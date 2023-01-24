# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.config import Config
from taipy.config.section import Section

from ..common._warnings import _warn_deprecated
from .data_node_config import DataNodeConfig


class TaskConfig(Section):
    """
    Holds all the configuration fields needed to create an actual `Task^` from the `TaskConfig`.

    Attributes:
        id (str): Identifier of the task config. Must be a valid Python variable name.
        inputs (Union[DataNodeConfig^, List[DataNodeConfig^]]): The optional list of `DataNodeConfig^` inputs. The
            default value is [].
        outputs (Union[DataNodeConfig^, List[DataNodeConfig^]]): The optional list of `DataNodeConfig^` outputs. The
            default value is [].
        skippable (bool): If True, indicates that the task can be skipped if no change has been made on inputs. The
            default value is _False_.
        function (Callable): User function taking as inputs some parameters compatible with the exposed types
            (_exposed_type_ field) of the input data nodes and returning results compatible with the exposed types
            (_exposed_type_ field) of the outputs list. The default value is None.
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    name = "TASK"

    _INPUT_KEY = "inputs"
    _FUNCTION = "function"
    _OUTPUT_KEY = "outputs"
    _IS_SKIPPABLE_KEY = "skippable"

    def __init__(
        self,
        id: str,
        function,
        inputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        outputs: Union[DataNodeConfig, List[DataNodeConfig]] = None,
        skippable: Optional[bool] = False,
        **properties,
    ):
        if inputs:
            self._inputs = [inputs] if isinstance(inputs, DataNodeConfig) else copy(inputs)
        else:
            self._inputs = []
        if outputs:
            self._outputs = [outputs] if isinstance(outputs, DataNodeConfig) else copy(outputs)
            outputs_all_cacheable = all(output.cacheable for output in self._outputs)
            if not skippable and outputs_all_cacheable:
                _warn_deprecated("cacheable", suggest="the skippable feature")
                skippable = True
        else:
            self._outputs = []
        self._skippable = skippable
        self.function = function
        super().__init__(id, **properties)

    def __copy__(self):
        return TaskConfig(self.id, copy(self._inputs), self.function, copy(self._outputs), **copy(self._properties))

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def input_configs(self) -> List[DataNodeConfig]:
        return list(self._inputs)

    @property
    def inputs(self) -> List[DataNodeConfig]:
        return list(self._inputs)

    @property
    def output_configs(self) -> List[DataNodeConfig]:
        return list(self._outputs)

    @property
    def outputs(self) -> List[DataNodeConfig]:
        return list(self._outputs)

    @property
    def skippable(self):
        return _tpl._replace_templates(self._skippable)

    @classmethod
    def default_config(cls):
        return TaskConfig(cls._DEFAULT_KEY, None, [], [], False)

    def _to_dict(self):
        return {
            self._INPUT_KEY: self._inputs,
            self._FUNCTION: self.function,
            self._OUTPUT_KEY: self._outputs,
            self._IS_SKIPPABLE_KEY: self._skippable,
            **self._properties,
        }

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):
        as_dict.pop(cls._ID_KEY, id)
        funct = as_dict.pop(cls._FUNCTION, None)
        dn_configs = config._sections[DataNodeConfig.name]  # type: ignore
        inputs = []
        if inputs_as_str := as_dict.pop(cls._INPUT_KEY, None):
            inputs = [dn_configs[dn_id] for dn_id in inputs_as_str if dn_id in dn_configs]
        outputs = []
        if outputs_as_str := as_dict.pop(cls._OUTPUT_KEY, None):
            outputs = [dn_configs[ds_id] for ds_id in outputs_as_str if ds_id in dn_configs]
        skippable = as_dict.pop(cls._IS_SKIPPABLE_KEY, False)
        return TaskConfig(id=id, function=funct, inputs=inputs, outputs=outputs, skippable=skippable, **as_dict)

    def _update(self, as_dict, default_section=None):
        self._inputs = as_dict.pop(self._INPUT_KEY, self._inputs)
        if self._inputs is None and default_section:
            self._inputs = default_section._inputs
        self._outputs = as_dict.pop(self._OUTPUT_KEY, self._outputs)
        if self._outputs is None and default_section:
            self._outputs = default_section._outputs
        function = as_dict.pop(self._FUNCTION, None)
        if function is not None and type(function) is not str:
            self.function = function
        self._skippable = as_dict.pop(self._IS_SKIPPABLE_KEY, self._skippable)
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(
        id: str,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: Optional[bool] = False,
        **properties,
    ):
        """Configure a new task configuration.

        Parameters:
            id (str): The unique identifier of this task configuration.
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            skippable (bool): If True, indicates that the task can be skipped if no change has
                been made on inputs. The default value is _False_.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `TaskConfig^`: The new task configuration.
        """
        section = TaskConfig(id, function, input, output, skippable, **properties)
        Config._register(section)
        return Config.sections[TaskConfig.name][id]

    @staticmethod
    def _configure_default(
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: Optional[bool] = False,
        **properties,
    ):
        """Configure the default values for task configurations.

        This function creates the _default task configuration_ object,
        where all task configuration objects will find their default
        values when needed.

        Parameters:
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            skippable (bool): If True, indicates that the task can be skipped if no change has
                been made on inputs. The default value is _False_.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `TaskConfig^`: The default task configuration.
        """
        section = TaskConfig(_Config.DEFAULT_KEY, function, input, output, skippable, **properties)
        Config._register(section)
        return Config.sections[TaskConfig.name][_Config.DEFAULT_KEY]
