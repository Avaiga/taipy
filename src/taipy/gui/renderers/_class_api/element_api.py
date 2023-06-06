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

from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

from .factory import _ClassApiFactory

if t.TYPE_CHECKING:
    from ...gui import Gui


class ElementApi(ABC):
    def __init__(self, **kwargs):
        self._properties = kwargs
        self._children = []

    def add(self, *elements: ElementApi):
        self._children.extend(elements)
        return self

    def _render(self, gui: "Gui") -> str:
        return ""
