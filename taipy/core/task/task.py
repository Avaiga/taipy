import uuid
from typing import Dict, Iterable, Optional

from taipy.core.common.alias import TaskId
from taipy.core.common.unicode_to_python_variable_name import protect_name
from taipy.core.data.data_node import DataNode
from taipy.core.data.scope import Scope


class Task:
    """Holds user function that will be executed, its parameters qs data nodes and outputs as data nodes.

    This element bring together the user code as function, parameters and outputs.

    Attributes:
        config_id: Identifier of the task configuration.
            We strongly recommend to use lowercase alphanumeric characters,
            dash character '-', or underscore character '_'.
            Note that other characters are replaced according the following rules :
            - Space character ' ' is replaced by '_'.
            - Unicode characters are replaced by a corresponding alphanumeric character using unicode library.
            - Other characters are replaced by dash character '-'.
        input:
            Data node input as list.
        function:
            Taking data from input data node and return data that should go inside of the output data node.
        output:
            Data node output result of the function as optional list.
        id:
            Unique identifier of this task. Generated if `None`.
        parent_id:
            Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
    """

    ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        config_id: str,
        function,
        input: Optional[Iterable[DataNode]] = None,
        output: Optional[Iterable[DataNode]] = None,
        id: TaskId = None,
        parent_id: Optional[str] = None,
    ):
        self.config_id = protect_name(config_id)
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self.ID_PREFIX, self.config_id, str(uuid.uuid4())]))
        self.parent_id = parent_id
        self.__input = {dn.config_id: dn for dn in input or []}
        self.__output = {dn.config_id: dn for dn in output or []}
        self.function = function

    def __hash__(self):
        return hash(self.id)

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    @property
    def output(self) -> Dict[str, DataNode]:
        return self.__output

    @property
    def input(self) -> Dict[str, DataNode]:
        return self.__input

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
        if protected_attribute_name in self.input:
            return self.input[protected_attribute_name]
        if protected_attribute_name in self.output:
            return self.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of task {self.id}")

    @property
    def scope(self) -> Scope:
        """Retrieve the lowest scope of the task based on its data node.

        Returns:
           Lowest `scope` present in input and output data node or GLOBAL if there are no neither input or output.
        """
        data_nodes = list(self.input.values()) + list(self.output.values())
        scope = min(dn.scope for dn in data_nodes) if len(data_nodes) != 0 else Scope.GLOBAL
        return Scope(scope)
