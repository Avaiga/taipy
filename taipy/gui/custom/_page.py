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

from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

import pandas as pd

from ..page import Page as BasePage
from ..utils import _TaipyData
from ..utils.singleton import _Singleton


class Page(BasePage):
    """NOT DOCUMENTED
    A custom page for external application that can be added to Taipy GUI"""

    def __init__(
        self,
        resource_handler: ResourceHandler,
        binding_variables: t.Optional[t.List[str]] = None,
        metadata: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs,
    ) -> None:
        if binding_variables is None:
            binding_variables = []
        if metadata is None:
            metadata = {}
        super().__init__(**kwargs)
        self._resource_handler = resource_handler
        self._binding_variables = binding_variables
        self._metadata: t.Dict[str, t.Any] = metadata


class ResourceHandler(ABC):
    """NOT DOCUMENTED
    Resource handler for custom pages.

    User can implement this class to provide custom resources for the custom pages
    """

    rh_id: str = ""

    data_layer_supported_types: t.Tuple[t.Type, ...] = (_TaipyData, pd.DataFrame, pd.Series)

    def __init__(self) -> None:
        _ExternalResourceHandlerManager().register(self)

    def get_id(self) -> str:
        return self.rh_id if self.rh_id != "" else str(id(self))

    @abstractmethod
    def get_resources(self, path: str, taipy_resource_path: str, base_url: str) -> t.Any:
        raise NotImplementedError


class _ExternalResourceHandlerManager(object, metaclass=_Singleton):
    """NOT DOCUMENTED
    Manager for resource handlers.

    This class is used to manage resource handlers for custom pages
    """

    def __init__(self) -> None:
        self.__handlers: t.Dict[str, ResourceHandler] = {}

    def register(self, handler: ResourceHandler) -> None:
        """Register a resource handler
        Arguments:
            handler (ResourceHandler): The resource handler to register
        """
        self.__handlers[handler.get_id()] = handler

    def get(self, id: str) -> t.Optional[ResourceHandler]:
        """Get a resource handler by its id
        Arguments:
            id (str): The id of the resource handler
        Returns:
            ResourceHandler: The resource handler
        """
        return self.__handlers.get(id, None)

    def get_all(self) -> t.List[ResourceHandler]:
        """Get all resource handlers
        Returns:
            List[ResourceHandler]: The list of resource handlers
        """
        return list(self.__handlers.values())
