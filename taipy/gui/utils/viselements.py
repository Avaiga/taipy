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
from copy import deepcopy


class VisElementProperties(t.TypedDict):
    name: str
    type: str
    doc: str
    default_value: t.Any
    default_property: t.Any


class VisElementDetail(t.TypedDict):
    inherits: t.List[str]
    properties: t.List[VisElementProperties]


VisElement = t.Tuple[str, VisElementDetail]


class VisElements(t.TypedDict):
    blocks: t.List[VisElement]
    controls: t.List[VisElement]
    undocumented: t.List[VisElement]


def _resolve_inherit_property(element: VisElement, viselements: VisElements) -> t.List[VisElementProperties]:
    element_detail = element[1]
    properties = deepcopy(element_detail["properties"])
    if "inherits" not in element_detail:
        return properties
    for inherit in element_detail["inherits"]:
        inherit_element = None
        for element_type in "blocks", "controls", "undocumented":
            inherit_element = next((e for e in viselements[element_type] if e[0] == inherit), None)  # type: ignore[literal-required]
            if inherit_element is not None:
                break
        if inherit_element is None:
            raise RuntimeError(f"Error resolving inherit element with name {inherit} in viselements.json")
        properties = properties + _resolve_inherit_property(inherit_element, viselements)
    return properties


def resolve_inherits(viselements: VisElements) -> VisElements:
    """NOT DOCUMENTED"""
    for element_type in "blocks", "controls":
        for element in viselements[element_type]:  # type: ignore[literal-required]
            element[1]["properties"] = _resolve_inherit_property(element, viselements)
    return viselements
