# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from abc import ABC, abstractmethod
import typing as t
import warnings

from ..types import _AttributeType
from ..renderers.utils import _to_camel_case
from ..renderers.builder import _Builder

if t.TYPE_CHECKING:
    from ..gui import Gui


class ElementAttribute():
    """
    TODO
    """

    def __init__(self, name: str, attribute_type: _AttributeType, default_value: t.Optional[t.Any], js_name: t.Optional[str] = None) -> None:
        self.name = name
        self.attribute_type = attribute_type
        self.default_value = default_value
        self.js_name = js_name
        super().__init__()
    
    def _get_js_name(self) -> str:
        return self.js_name or _to_camel_case(self.name)

    def check(self, control: str):
        if not isinstance(self.name, str) or not self.name or not self.name.isidentifier():
            warnings.warn(f"Element '{control}' should have a valid attribute name '{self.name}'")
        if not isinstance(self.attribute_type, _AttributeType):
            warnings.warn(f"Element Attribute '{control}.{self.name}' should have a valid type '{self.attribute_type}'")
    
    def _get_tuple(self) -> tuple:
        return (self.name, self.attribute_type, self.default_value)


class Element():
    """
    TODO
    """
    
    def __init__(self, name: str, default_attribute: str, attributes: t.List[ElementAttribute], js_name: t.Optional[str] = None) -> None:
        self.name = name
        self.default_attribute = default_attribute
        self.attributes = attributes
        self.js_name = js_name
        super().__init__()

    def _get_js_name(self) -> str:
        return self.js_name or _to_camel_case(self.name)

    def check(self):
        if not isinstance(self.name, str) or not self.name or not self.name.isidentifier():
            warnings.warn(f"Element should have a valid name '{self.name}'")
        default_found = False
        for attr in self.attributes:
            if isinstance(attr, ElementAttribute):
                attr.check(self.name)
                if not default_found:
                    default_found = self.default_attribute == attr.name
            else:
                warnings.warn(f"Attribute should inherit from 'ElementAttribute' '{self.name}.{attr}'")
        if not default_found:
            warnings.warn(f"User Default Attribute should be describe in the 'attributes' List '{self.name}{self.default_attribute}'")
    
    def _call_builder(self, gui: "Gui", all_properties: t.Optional[t.Dict[str, t.Any]], is_html: t.Optional[bool] = False) -> t.Union[t.Any, t.Tuple[str, str]]:
        res = self.render(gui, all_properties, is_html)
        if res is None:
            default_attr: t.Optional[ElementAttribute] = None
            attrs = []
            for ua in self.attributes:
                if isinstance(ua, ElementAttribute):
                    if self.default_attribute == ua.name:
                        default_attr = ua
                    else:
                        attrs.append(ua._get_tuple())
            build = _Builder(
                gui=gui,
                control_type=self.name,
                element_name=self._get_js_name(),
                attributes=all_properties,
            )
            if default_attr is not None:
                build.set_value_and_default(var_name=default_attr.name, var_type = default_attr.attribute_type, default_val=default_attr.default_value)
            builded = build.set_attributes(attrs)
            return builded.build_to_string() if is_html else builded.el
        else:
            return res
    
    def render(self, gui: "Gui", all_properties: t.Optional[t.Dict[str, t.Any]], is_html: t.Optional[bool] = False)-> t.Union[None, t.Any, t.Tuple[str, str]]:
        """
        TODO
        """
        return None

class ElementLibrary(ABC):
    """
    TODO
    """
    
    @abstractmethod
    def get_elements(self) -> t.List[Element]:
        """
        TODO
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        TODO
        """
        pass