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

import typing as t
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

from ..renderers.builder import Builder
from ..renderers.utils import _to_camel_case
from ..types import PropertyType

if t.TYPE_CHECKING:
    from ..gui import Gui


class ElementAttribute:
    """
    TODO
    This is instantiated to describe an element attribute.
    """

    def __init__(
        self,
        name: str,
        attribute_type: PropertyType,
        default_value: t.Optional[t.Any] = None,
        js_name: t.Optional[str] = None,
    ) -> None:
        """
        Arguments:

            name (str): The attribute name.
            attribute_type (PropertyType): The attribute type.
            default_value (optional Any): The attribute's default value (default is None).
            js_name (optional str): The name of the attribute on the frontend (default to Camel Case of `name`).
                Attribute starting with `on_<action name>` will be translated into `tp_on<CamelCase(action name)>`.

        """
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
        if not isinstance(self.attribute_type, PropertyType):
            warnings.warn(f"Element Attribute '{control}.{self.name}' should have a valid type '{self.attribute_type}'")

    def _get_tuple(self) -> tuple:
        return (self.name, self.attribute_type, self.default_value)


class Element:
    """
    TODO
    This is instantiated to describe an element.

    """

    def __init__(
        self, name: str, default_attribute: str, attributes: t.List[ElementAttribute], js_name: t.Optional[str] = None
    ) -> None:
        """
        Arguments:

            name (str): The element name.
            default_attribute (str): the default attribute for the element.
            attributes (List[ElementAttribute]): A list of attributes.
            js_name (optional str): The name of the element on the frontend (default to Camel Case of `name`).
        """
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
        for attr in self.attributes or []:
            if isinstance(attr, ElementAttribute):
                attr.check(self.name)
                if not default_found:
                    default_found = self.default_attribute == attr.name
            else:
                warnings.warn(f"Attribute should inherit from 'ElementAttribute' '{self.name}.{attr}'")
        if not default_found:
            warnings.warn(
                f"User Default Attribute should be describe in the 'attributes' List '{self.name}{self.default_attribute}'"
            )

    def _call_builder(
        self,
        gui: "Gui",
        properties: t.Union[t.Dict[str, t.Any], None],
        lib_name: str,
        is_html: t.Optional[bool] = False,
    ) -> t.Union[t.Any, t.Tuple[str, str]]:
        attributes = properties or {}
        hash_names = Builder._get_variable_hash_names(gui, attributes)
        default_attr: t.Optional[ElementAttribute] = None
        default_value = None
        attrs = []
        for ua in self.attributes or []:
            if isinstance(ua, ElementAttribute):
                if self.default_attribute == ua.name:
                    default_attr = ua
                    default_value = ua.default_value
                else:
                    attrs.append(ua._get_tuple())
        elt_built = Builder(
            gui=gui,
            control_type=self.name,
            element_name=self._get_js_name(),
            attributes=properties,
            hash_names=hash_names,
            lib_name=lib_name,
            default_value=default_value,
        )
        if default_attr is not None:
            elt_built.set_value_and_default(
                var_name=default_attr.name,
                var_type=default_attr.attribute_type,
                default_val=default_attr.default_value,
                with_default=default_attr.attribute_type != PropertyType.data,
            )
        elt_built.set_attributes(attrs)
        # call user render
        self.render(gui, attributes, hash_names, elt_built)
        return elt_built._build_to_string() if is_html else elt_built.el

    def render(self, gui: "Gui", properties: t.Dict[str, t.Any], hash_names: t.Dict[str, str], builder: Builder):
        """
        TODO
        Uses the builder to update the xml node

        Arguments:

            gui (Gui): The current instance of Gui.
            properties (t.Dict[str, t.Any]): The dict containing a value for each defined attribute.
            hash_names (t.Dict[str, str]): The dict containing the internal variable name for each bound attribute.

        Returns: (void)
        """


class ElementLibrary(ABC):
    """
    TODO
    This class needs to be inherited to define a new library.

    """

    @abstractmethod
    def get_elements(self) -> t.List[Element]:
        """
        TODO
        Returns the list of visual elements.
        """
        return NotImplemented

    @abstractmethod
    def get_name(self) -> str:
        """
        TODO
        Returns the library name.
        """
        return NotImplemented

    @abstractmethod
    def get_scripts(self) -> t.List[str]:
        """
        TODO
        Returns the list of resources names for the scripts.
        """
        return NotImplemented

    @abstractmethod
    def get_styles(self) -> t.List[str]:
        """
        TODO
        Returns the list of resources names for the css stylesheets.

        """
        return NotImplemented

    @abstractmethod
    def get_resource(self, name: str) -> Path:
        """
        TODO
        Returns a path for a resource name.

        Arguments:

            name (str): The name of the resource for which a local Path should be returned.
        """
        return NotImplemented

    @abstractmethod
    def get_register_js_function(self) -> str:
        """
        TODO
        Returns the name of the function that will register new js components.
            signature (libName: string) => Record<string, ComponentType>
        """
        return NotImplemented

    def get_data(self, library_name: str, payload: t.Dict, var_name: str, value: t.Any) -> t.Optional[t.Dict]:
        """
        TODO
        Called if implemented (ie returns a dict).

        Arguments:

            library_name (str): The name of this library.
            payload (t.Dict): The payload send by the `createRequestDataUpdateAction` frontend function.
            var_name (str): The name of the variable holding the data.
            value (t.Any): The current value of the variable identified by `var_name`.
        """
        return None
