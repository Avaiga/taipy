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
import xml.etree.ElementTree as etree
from abc import ABC, abstractmethod
from pathlib import Path

from ..renderers.builder import _Builder
from ..renderers.utils import _to_camel_case
from ..types import PropertyType

if t.TYPE_CHECKING:
    from ..gui import Gui


class ElementProperty:
    """
    The declaration of a property of a visual element.

    Each visual element property is described by an instance of `ElementProperty`.
    This class holds the information on the name, type and default value for the
    element property.
    """

    def __init__(
        self,
        property_type: PropertyType,
        default_value: t.Optional[t.Any] = None,
        js_name: t.Optional[str] = None,
    ) -> None:
        """Initializes a new custom property declaration for an `Element^`.

        Arguments:
            property_type (PropertyType): The type of this property.
            default_value (Optional[Any]): The default value for this property. Default is None.
            js_name (Optional[str]): The name of this property, in the front-end JavaScript code.<br/>
                If unspecified, a camel case version of `name` is generated: for example, if `name` is
                "my_property_name", then this property is referred to as "myPropertyName" in the
                JavaScript code.
        """
        self.property_type = property_type
        self.default_value = default_value
        self._js_name = js_name
        super().__init__()

    def check(self, element_name: str, prop_name: str):
        if not isinstance(prop_name, str) or not prop_name or not prop_name.isidentifier():
            warnings.warn(f"Property name '{prop_name}' is invalid for element '{element_name}'.")
        if not isinstance(self.property_type, PropertyType):
            warnings.warn(
                f"Property type '{self.property_type}' is invalid for element property '{element_name}.{prop_name}'."
            )

    def _get_tuple(self, name: str) -> tuple:
        return (name, self.property_type, self.default_value)

    def get_js_name(self, name: str) -> str:
        return self._js_name or _to_camel_case(name)


class Element:
    """
    The definition of a custom visual element.

    An element is defined by its properties (name, type and default value) and
    what the default property name is.
    """

    def __init__(
        self,
        default_property: str,
        properties: t.Dict[str, ElementProperty],
        react_component: t.Optional[str] = None,
        render_xhtml: t.Optional[t.Callable[[t.Dict[str, t.Any]], str]] = None,
    ) -> None:
        """Initializes a new custom element declaration.

        Arguments:
            default_property (str): the default property for this element.
            properties (List[ElementProperty]): The list of properties for this element.
            react_component (Optional[str]): The name of the component to be created on the frontend
                If not specified, it is set to a camel case version of `name` (one_name => OneName).
            render_xhtml (Optional[callable[[dict[str, Any]], str]]): A function that receives a
                dict containing the element's properties and their values
                and that returns a valid XHTML string.
        """
        self.default_attribute = default_property
        self.attributes = properties
        self.js_name = react_component
        if callable(render_xhtml):
            self._render_xhtml = render_xhtml
        super().__init__()

    def _get_js_name(self, name: str) -> str:
        return self.js_name or _to_camel_case(name, True)

    def check(self, name: str):
        if not isinstance(name, str) or not name or not name.isidentifier():
            warnings.warn(f"Invalid element name: '{name}'.")
        default_found = False
        if self.attributes:
            for prop_name, property in self.attributes.items():
                if isinstance(property, ElementProperty):
                    property.check(name, prop_name)
                    if not default_found:
                        default_found = self.default_attribute == prop_name
                else:
                    warnings.warn(f"Property must inherit from 'ElementProperty' '{name}.{prop_name}'.")
        if not default_found:
            warnings.warn(f"Element {name} has no default property.")

    def _is_server_only(self):
        return hasattr(self, "_render_xhtml") and callable(self._render_xhtml)

    def _call_builder(
        self,
        name,
        gui: "Gui",
        properties: t.Union[t.Dict[str, t.Any], None],
        lib: "ElementLibrary",
        is_html: t.Optional[bool] = False,
    ) -> t.Union[t.Any, t.Tuple[str, str]]:
        attributes = properties or {}
        hash_names = _Builder._get_variable_hash_names(gui, attributes)  # variable replacement
        # call user render if any
        if self._is_server_only():
            xhtml = self._render_xhtml(attributes)
            try:
                xml_root = etree.fromstring(xhtml)
                if is_html:
                    return xhtml, name
                else:
                    return xml_root

            except Exception as e:
                warnings.warn(f"{name}.render_xhtml() did not return a valid XHTML string.\n{e}")
                return f"{name}.render_xhtml() did not return a valid XHTML string. {e}"
        else:
            default_attr: t.Optional[ElementProperty] = None
            default_value = None
            default_name = None
            attrs = []
            if self.attributes:
                for prop_name, property in self.attributes.items():
                    if isinstance(property, ElementProperty):
                        if self.default_attribute == prop_name:
                            default_name = prop_name
                            default_attr = property
                            default_value = property.default_value
                        else:
                            attrs.append(property._get_tuple(prop_name))
            elt_built = _Builder(
                gui=gui,
                control_type=name,
                element_name=f"{lib.get_js_module_name()}_{self._get_js_name(name)}",
                attributes=properties,
                hash_names=hash_names,
                lib_name=lib.get_name(),
                default_value=default_value,
            )
            if default_attr is not None:
                elt_built.set_value_and_default(
                    var_name=default_name,
                    var_type=default_attr.property_type,
                    default_val=default_attr.default_value,
                    with_default=default_attr.property_type != PropertyType.data,
                )
            elt_built.set_attributes(attrs)
            return elt_built._build_to_string() if is_html else elt_built.el


class ElementLibrary(ABC):
    """
    A library of user-defined visual elements.

    TODO
    """

    @abstractmethod
    def get_elements(self) -> t.Dict[str, Element]:
        """
        Returns the dict of all visual element declarations.
        TODO
        The default implementation returns an empty dict, indicating that this library contains
        no custom visual elements.
        """
        return {}

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the library name.

        TODO:
        - What is this name used for?
        - What if two libraries with the same same get added to the Gui?
        """
        return NotImplemented

    def get_js_module_name(self) -> str:
        """
        Returns the name of the Javascript module.

        Typically, Javascript module names use camel case.

        This module name must be unique on the browser window scope.

        TODO
        Returns:
            The name of the Javascript module.<br/>
            The default implementation returns camel case of `self.get_name()`.
        """
        return _to_camel_case(self.get_name(), True)

    def get_scripts(self) -> t.List[str]:
        """
        Returns the list of resources names for the scripts.

        The default implementation returns an empty list, indicating that this library contains
        no custom visual elements.
        TODO: Clarify - this is wrong:
            May be this should return some <lib_name>.js...
        """
        return []

    def get_styles(self) -> t.List[str]:
        """
        TODO
        Returns the list of resources names for the css stylesheets.
        Defaults to []

        """
        return []

    def get_resource(self, name: str) -> Path:
        """
        TODO
        Defaults to return None?
        Returns a path for a resource name.
        Resource URL should be formed as /taipy-extension/<library_name>/<resource virtual path> with(see get_resource_url)
        - <resource virtual path> being the `name` parameter
        - <library_name> the value returned by `get_name()`

        Arguments:

            name (str): The name of the resource for which a local Path should be returned.
        """
        module = self.__class__.__module__
        base = (Path(module.__file__) if hasattr(module, "__file__") else Path(".")).resolve()  # type: ignore
        file = (base / name).resolve()
        if str(file).startswith(str(base)) and file.exists():
            return file
        else:
            raise FileNotFoundError(f"Cannot access resource {file}.")

    def get_resource_url(self, resource: str) -> str:
        """TODO"""
        from ..gui import Gui

        return f"{Gui._EXTENSION_ROOT}{self.get_name()}/{resource}"

    def get_data(self, library_name: str, payload: t.Dict, var_name: str, value: t.Any) -> t.Optional[t.Dict]:
        """
        TODO
        Called if implemented (ie returns a dict).

        Arguments:

            library_name (str): The name of this library.
            payload (dict): The payload send by the `createRequestDataUpdateAction()` frontend function.
            var_name (str): The name of the variable holding the data.
            value (any): The current value of the variable identified by *var_name*.
        """
        return None
