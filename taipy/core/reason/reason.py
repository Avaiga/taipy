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

from typing import Any, Optional


class Reason:
    """
    A reason holds the reason why specific actions cannot be performed.

    Attributes:
        reason (str): The reason why the action cannot be performed.
    """

    def __init__(self, reason: str):
        self._reason = reason

    @property
    def reason(self) -> str:
        return self._reason

    def __str__(self) -> str:
        return self._reason

    def __repr__(self) -> str:
        return self._reason

    def __hash__(self) -> int:
        return hash(self._reason)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Reason) and value._reason == self._reason


class _DataNodeReasonMixin:
    def __init__(self, datanode_id: str):
        self.datanode_id = datanode_id

    @property
    def datanode(self):
        from ..data._data_manager_factory import _DataManagerFactory

        return _DataManagerFactory._build_manager()._get(self.datanode_id)


class DataNodeEditInProgress(Reason, _DataNodeReasonMixin):
    """
    DataNodeEditInProgress holds the reason a `DataNode^` is being edited,
    which prevents specific actions from being performed.

    Attributes:
        datanode_id (str): The identifier of the `DataNode^`.
    """

    def __init__(self, datanode_id: str):
        Reason.__init__(self, f"DataNode {datanode_id} is being edited")
        _DataNodeReasonMixin.__init__(self, datanode_id)


class DataNodeIsNotWritten(Reason, _DataNodeReasonMixin):
    """
    DataNodeIsNotWritten holds the reason a `DataNode^` is not yet written,
    which prevents specific actions from being performed.

    Attributes:
        datanode_id (str): The identifier of the `DataNode^`.
    """

    def __init__(self, datanode_id: str):
        Reason.__init__(self, f"DataNode {datanode_id} is not written")
        _DataNodeReasonMixin.__init__(self, datanode_id)


class EntityIsNotSubmittableEntity(Reason):
    """
    EntityIsNotSubmittableEntity holds the reason an entity is not submittable.

    Attributes:
        entity_id (str): The identifier of the `Entity^`.
    """

    def __init__(self, entity_id: str):
        Reason.__init__(self, f"Entity {entity_id} is not a submittable entity")


class WrongConfigType(Reason):
    """
    WrongConfigType holds the reason the provided config is not the valid config expected.

    Attributes:
        config_id (str): The identifier of the config.
        config_type (str): The expected config type.
    """

    def __init__(self, config_id: str, config_type: Optional[str]):
        if config_type:
            reason = f'Object "{config_id}" must be a valid {config_type}'
        else:
            reason = f'Object "{config_id}" is not a valid config to be created'

        Reason.__init__(self, reason)


class NotGlobalScope(Reason):
    """
    NotGlobalScope holds the reason the data node config does not have a GLOBAL scope,
    which prevents certain actions from being performed.

    Attributes:
        config_id (str): The identifier of the config.
    """

    def __init__(self, config_id: str):
        Reason.__init__(self, f'Data node config "{config_id}" does not have GLOBAL scope')
