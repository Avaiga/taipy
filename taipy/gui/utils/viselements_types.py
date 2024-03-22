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

import typing as t


class VisElementProperties(t.TypedDict, total=False):
    name: str
    type: str
    doc: str
    default_value: t.Any
    default_property: t.Any


class VisElementDetail(t.TypedDict, total=False):
    inherits: t.List[str]
    properties: t.List[VisElementProperties]


VisElement: t.TypeAlias = t.Tuple[str, VisElementDetail]


class VisElements(t.TypedDict):
    blocks: t.List[VisElement]
    controls: t.List[VisElement]
    undocumented: t.List[VisElement]
