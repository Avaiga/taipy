# Copyright 2021-2024 Avaiga Private Limited
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
from typing import Any, Callable, Dict, List, Optional, Union, cast

from taipy.common.config import Config
from taipy.common.config._config import _Config
from taipy.common.config.common._template_handler import _TemplateHandler as _tpl
from taipy.common.config.section import Section

from .data_node_config import DataNodeConfig


class TaskConfig(Section):
    """Configuration fields needed to instantiate an actual `Task^`."""

    # Attributes:
    #     inputs (Union[DataNodeConfig^, List[DataNodeConfig^]]): The optional list of
    #         `DataNodeConfig^` inputs.<br/>
    #         The default value is [].
    #     outputs (Union[DataNodeConfig^, List[DataNodeConfig^]]): The optional list of
    #         `DataNodeConfig^` outputs.<br/>
    #         The default value is [].
    #     skippable (bool): If True, indicates that the task can be skipped if no change has
    #         been made on inputs.<br/>
    #         The default value is False.
    #     function (Callable): User function taking as inputs some parameters compatible with the
    #         exposed types (*exposed_type* field) of the input data nodes and returning results
    #         compatible with the exposed types (*exposed_type* field) of the outputs list.<br/>
    #         The default value is None.

    name = "TASK"

    _INPUT_KEY = "inputs"
    _FUNCTION = "function"
    _OUTPUT_KEY = "outputs"
    _IS_SKIPPABLE_KEY = "skippable"

    function: Optional[Callable]
    """User function taking as inputs some parameters compatible with the data type
    (*exposed_type* field) of the input data nodes and returning results compatible with the
    data type (*exposed_type* field) of the outputs list."""

    def __init__(
        self,
        id: str,
        function: Optional[Callable],
        inputs: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        outputs: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: bool = False,
        **properties,
    ) -> None:
        if inputs:
            self._inputs = [inputs] if isinstance(inputs, DataNodeConfig) else copy(inputs)
        else:
            self._inputs = []
        if outputs:
            self._outputs = [outputs] if isinstance(outputs, DataNodeConfig) else copy(outputs)
        else:
            self._outputs = []
        self._skippable: bool = skippable
        self.function: Optional[Callable] = function
        super().__init__(id, **properties)

    def __copy__(self):
        return TaskConfig(
            self.id, self.function, copy(self._inputs), copy(self._outputs), self.skippable, **copy(self._properties)
        )

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def input_configs(self) -> List[DataNodeConfig]:
        """The list of the input data node configurations."""
        return list(self._inputs)

    @property
    def inputs(self) -> List[DataNodeConfig]:
        """The list of the input data node configurations."""
        return list(self._inputs)

    @property
    def output_configs(self) -> List[DataNodeConfig]:
        """The list of the output data node configurations."""
        return list(self._outputs)

    @property
    def outputs(self) -> List[DataNodeConfig]:
        """The list of the output data node configurations."""
        return list(self._outputs)

    @property
    def skippable(self) -> bool:
        """Indicates if the task can be skipped if no change has been made on inputs."""
        return _tpl._replace_templates(self._skippable)

    @classmethod
    def default_config(cls) -> "TaskConfig":
        """Get the default task configuration.

        Returns:
            The default task configuration.
        """
        return TaskConfig(cls._DEFAULT_KEY, None, [], [], False)

    def _clean(self) -> None:
        self.function = None
        self._inputs = []
        self._outputs = []
        self._skippable = False
        self._properties.clear()

    def _to_dict(self):
        return {
            self._FUNCTION: self.function,
            self._INPUT_KEY: self._inputs,
            self._OUTPUT_KEY: self._outputs,
            self._IS_SKIPPABLE_KEY: self._skippable,
            **self._properties,
        }

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):
        as_dict.pop(cls._ID_KEY, id)
        funct = as_dict.pop(cls._FUNCTION, None)
        dn_configs: Dict[str, DataNodeConfig] = {}
        if config:
            dn_configs = cast(Dict[str, DataNodeConfig], config._sections.get(DataNodeConfig.name))

        inputs: List[DataNodeConfig] = []
        if inputs_as_str := as_dict.pop(cls._INPUT_KEY, None):
            inputs = [dn_configs[dn_id] for dn_id in inputs_as_str if dn_id in dn_configs]
        outputs: List[DataNodeConfig] = []
        if outputs_as_str := as_dict.pop(cls._OUTPUT_KEY, None):
            outputs = [dn_configs[ds_id] for ds_id in outputs_as_str if ds_id in dn_configs]
        skippable = as_dict.pop(cls._IS_SKIPPABLE_KEY, False)
        return TaskConfig(id=id, function=funct, inputs=inputs, outputs=outputs, skippable=skippable, **as_dict)

    def _update(self, as_dict, default_section=None):
        function = as_dict.pop(self._FUNCTION, None)
        if function is not None and not isinstance(function, str):
            self.function = function
        self._inputs = as_dict.pop(self._INPUT_KEY, self._inputs)
        if self._inputs is None and default_section:
            self._inputs = default_section._inputs
        self._outputs = as_dict.pop(self._OUTPUT_KEY, self._outputs)
        if self._outputs is None and default_section:
            self._outputs = default_section._outputs
        self._skippable = as_dict.pop(self._IS_SKIPPABLE_KEY, self._skippable)
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(
        id: str,
        function: Optional[Callable],
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: bool = False,
        **properties,
    ) -> "TaskConfig":
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
                been made on inputs.<br/>
                The default value is False.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new task configuration.
        """
        section = TaskConfig(id, function, input, output, skippable, **properties)
        Config._register(section)
        return Config.sections[TaskConfig.name][id]

    @staticmethod
    def _set_default_configuration(
        function: Optional[Callable],
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: bool = False,
        **properties,
    ) -> "TaskConfig":
        """Set the default values for task configurations.

        This function creates the *default task configuration* object,
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
                been made on inputs.<br/>
                The default value is False.
            **properties (dict[str, any]): A keyworded variable length list of additional
                arguments.

        Returns:
            The default task configuration.
        """
        section = TaskConfig(_Config.DEFAULT_KEY, function, input, output, skippable, **properties)
        Config._register(section)
        return Config.sections[TaskConfig.name][_Config.DEFAULT_KEY]
