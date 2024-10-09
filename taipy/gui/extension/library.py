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

import re
import sys
import typing as t
import xml.etree.ElementTree as etree
from abc import ABC, abstractmethod
from inspect import isclass
from pathlib import Path
from urllib.parse import urlencode

from .._renderers.builder import _Builder
from .._warnings import _warn
from ..types import PropertyType
from ..utils import _get_broadcast_var_name, _TaipyBase, _to_camel_case

if t.TYPE_CHECKING:
    from ..gui import Gui
    from ..state import State


class ElementProperty:
    """
    The declaration of a property of a visual element.

    Each visual element property is described by an instance of `ElementProperty`.
    This class holds the information on the name, type and default value for the
    element property.
    """

    def __init__(
        self,
        property_type: t.Union[PropertyType, t.Type[_TaipyBase]],
        default_value: t.Optional[t.Any] = None,
        js_name: t.Optional[str] = None,
        with_update: t.Optional[bool] = None,
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
        self.default_value = default_value
        self.property_type: t.Union[PropertyType, t.Type[_TaipyBase]]
        if property_type == PropertyType.broadcast:
            if isinstance(default_value, str):
                self.default_value = _get_broadcast_var_name(default_value)
            else:
                _warn("Element property with type 'broadcast' must define a string default value.")
            self.property_type = PropertyType.react
        else:
            self.property_type = property_type
        self._js_name = js_name
        self.with_update = with_update
        super().__init__()

    def check(self, element_name: str, prop_name: str):
        if not isinstance(prop_name, str) or not prop_name or not prop_name.isidentifier():
            _warn(f"Property name '{prop_name}' is invalid for element '{element_name}'.")
        if not isinstance(self.property_type, PropertyType) and not (
            isclass(self.property_type) and issubclass(self.property_type, _TaipyBase)
        ):
            _warn(f"Property type '{self.property_type}' is invalid for element property '{element_name}.{prop_name}'.")

    def _get_tuple(self, name: str) -> tuple:
        return (
            (name, self.property_type, self.default_value)
            if self.with_update is None
            else (name, self.property_type, self.default_value, self.with_update)
        )

    def get_js_name(self, name: str) -> str:
        return self._js_name or _to_camel_case(name)


class Element:
    """
    The definition of a custom visual element.

    An element is defined by its properties (name, type and default value) and
    what the default property name is.
    """

    __RE_PROP_VAR = re.compile(r"<tp:prop:(\w+)>")
    __RE_UNIQUE_VAR = re.compile(r"<tp:uniq:(\w+)>")

    def __init__(
        self,
        default_property: str,
        properties: t.Dict[str, ElementProperty],
        react_component: t.Optional[str] = None,
        render_xhtml: t.Optional[t.Callable[[t.Dict[str, t.Any]], str]] = None,
        inner_properties: t.Optional[t.Dict[str, ElementProperty]] = None,
    ) -> None:
        """Initializes a new custom element declaration.

        If *render_xhtml* is specified, then this is a static element, and
        *react_component* is ignored.

        Arguments:
            default_property (str): The name of the default property for this element.
            properties (Dict[str, ElementProperty]): The dictionary containing the properties of this element, where the keys are the property names and the values are instances of ElementProperty.
            inner_properties (Optional[List[ElementProperty]]): The optional list of inner properties for this element.<br/>
                Default values are set/binded automatically.
            react_component (Optional[str]): The name of the component to be created on the front-end.<br/>
                If not specified, it is set to a camel case version of the element's name
                ("one_name" is transformed to "OneName").
            render_xhtml (Optional[callable[[dict[str, Any]], str]]): A function that receives a
                dictionary containing the element's properties and their values
                and that must return a valid XHTML string.
        """  # noqa: E501
        self.default_attribute = default_property
        self.attributes = properties
        self.inner_properties = inner_properties
        self.js_name = react_component
        if callable(render_xhtml):
            self._render_xhtml = render_xhtml
        super().__init__()

    def _get_js_name(self, name: str) -> str:
        return self.js_name or _to_camel_case(name, True)

    def check(self, name: str):
        if not isinstance(name, str) or not name or not name.isidentifier():
            _warn(f"Invalid element name: '{name}'.")
        default_found = False
        if self.attributes:
            for prop_name, property in self.attributes.items():
                if isinstance(property, ElementProperty):
                    property.check(name, prop_name)
                    if not default_found:
                        default_found = self.default_attribute == prop_name
                else:
                    _warn(f"Property must inherit from 'ElementProperty' '{name}.{prop_name}'.")
        if not default_found:
            _warn(f"Element {name} has no default property.")

    def _is_server_only(self):
        return hasattr(self, "_render_xhtml") and callable(self._render_xhtml)

    def _call_builder(
        self,
        name,
        gui: "Gui",
        properties: t.Optional[t.Dict[str, t.Any]],
        lib: "ElementLibrary",
        is_html: t.Optional[bool] = False,
        counter: int = 0,
    ) -> t.Union[t.Any, t.Tuple[str, str]]:
        attributes = properties if isinstance(properties, dict) else {}
        if self.inner_properties:
            uniques: t.Dict[str, int] = {}
            self.attributes.update(
                {
                    prop: ElementProperty(attr.property_type, None, attr._js_name, attr.with_update)
                    for prop, attr in self.inner_properties.items()
                }
            )
            for prop, attr in self.inner_properties.items():
                val = attr.default_value
                if val:
                    # handling property replacement in inner properties <tp:prop:...>
                    while m := Element.__RE_PROP_VAR.search(val):
                        var = attributes.get(m.group(1))
                        hash_value = None if var is None else gui._evaluate_expr(var)
                        if hash_value:
                            names = gui._get_real_var_name(hash_value)
                            hash_value = names[0] if isinstance(names, tuple) else names
                        else:
                            hash_value = "None"
                        val = val[: m.start()] + hash_value + val[m.end() :]
                    # handling unique id replacement in inner properties <tp:uniq:...>
                    has_uniq = False
                    while m := Element.__RE_UNIQUE_VAR.search(val):
                        has_uniq = True
                        id = uniques.get(m.group(1))
                        if id is None:
                            id = len(uniques) + 1
                            uniques[m.group(1)] = id
                        val = f"{val[: m.start()]}{counter}{id}{val[m.end() :]}"
                    if has_uniq and gui._is_expression(val):
                        gui._evaluate_expr(val, True)

                attributes[prop] = val
        # this modifies attributes
        hash_names = _Builder._get_variable_hash_names(gui, attributes)  # variable replacement
        # call user render if any
        if self._is_server_only():
            xhtml = self._render_xhtml(attributes)
            try:
                xml_root = etree.fromstring(xhtml)
                return (xhtml, name) if is_html else xml_root

            except Exception as e:
                _warn(f"{name}.render_xhtml() did not return a valid XHTML string", e)
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
                    var_type=t.cast(PropertyType, default_attr.property_type),
                    default_val=default_attr.default_value,
                    with_default=default_attr.property_type != PropertyType.data,
                )
            elt_built.set_attributes(attrs)
            return elt_built._build_to_string() if is_html else elt_built.el


class ElementLibrary(ABC):
    """
    A library of user-defined visual elements.

    An element library can declare any number of custom visual elements.

    In order to use those elements you must register the element library
    using the function `Gui.add_library()^`.

    An element library can mix *static* and *dynamic* elements.
    """

    @abstractmethod
    def get_elements(self) -> t.Dict[str, Element]:
        """
        Return the dictionary holding all visual element declarations.

        The key for each of this dictionary's entry is the name of the element,
        and the value is an instance of `Element^`.

        The default implementation returns an empty dictionary, indicating that this library
        contains no custom visual elements.
        """
        return {}

    @abstractmethod
    def get_name(self) -> str:
        """
        Return the library name.

        This string is used for different purposes:

        - It allows for finding the definition of visual elements when parsing the
          page content.<br/>
          Custom elements are defined with the fragment `<|<library_name>.<element_name>|>` in
          Markdown pages, and with the tag `<<library_name>:<element_name>>` in HTML pages.

        - In element libraries that hold elements with dynamic properties (where JavaScript)
          is involved, the name of the JavaScript module that has the front-end code is
          derived from this name, as described in `(ElementLibrary.)get_js_module_name()^`.

        Returns:
            The name of this element library. This must be a valid Python identifier.

        !!! note "Element libraries with the same name"
            You can add different libraries that have the same name.<br/>
            This is useful in large projects where you want to split a potentially large number
            of custom visual elements into different groups but still access them from your pages
            using the same library name prefix.<br/>
            In this situation, you will have to implement `(ElementLibrary.)get_js_module_name()^`
            because each JavaScript module will have to have a unique name.

        """
        raise NotImplementedError

    def get_js_module_name(self) -> str:
        """
        Return the name of the JavaScript module.

        The JavaScript module is the JavaScript file that contains all the front-end
        code for this element library. Typically, the name of JavaScript modules uses camel case.<br/>
        This module name must be unique on the browser window scope: if your application uses
        several custom element libraries, they must define a unique name for their JavaScript module.

        The default implementation transforms the return value of `(ElementLibrary.)get_name()^` in
        the following manner:

        - The JavaScript module name is a camel case version of the element library name
          (see `(ElementLibrary.)get_name()^`):
            - If the library name is "library", the JavaScript module name defaults to "Library".
            - If the library name is "myLibrary", the JavaScript module name defaults to "Mylibrary".
        - If the element library name has underscore characters, each underscore-separated fragment is
          considered as a distinct word:
            - If the library name is "my_library", the JavaScript module name defaults to "MyLibrary".

        Returns:
            The name of the JavaScript module for this element library.<br/>
            The default implementation returns a camel case version of `self.get_name()`,
            as described above.
        """
        return _to_camel_case(self.get_name(), True)

    def get_scripts(self) -> t.List[str]:
        """
        Return the list of the mandatory script file pathnames.

        If a script file pathname is an absolute URL it will be used as is.<br/>
        If it's not it will be passed to `(ElementLibrary.)get_resource()^` to retrieve a local
        path to the resource.

        The default implementation returns an empty list, indicating that this library contains
        no custom visual elements with dynamic properties.

        Returns:
            A list of paths (relative to the element library Python implementation file or
            absolute) to all JavaScript module files to be loaded on the front-end.<br/>
            The default implementation returns an empty list.
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
        """  # noqa: E501
        module_obj = sys.modules.get(self.__class__.__module__)
        base = (Path(".") if module_obj is None else Path(module_obj.__file__).parent).resolve()  # type: ignore
        base = base if base.exists() else Path(".").resolve()
        file = (base / name).resolve()
        if str(file).startswith(str(base)) and file.exists():
            return file
        else:
            raise FileNotFoundError(f"Cannot access resource {file}.")

    def get_resource_url(self, resource: str) -> str:
        """TODO"""
        from ..gui import Gui

        return f"/{Gui._EXTENSION_ROOT}/{self.get_name()}/{resource}{self.get_query(resource)}"

    def get_data(self, library_name: str, payload: t.Dict, var_name: str, value: t.Any) -> t.Optional[t.Dict]:
        """
        TODO
        Called if implemented (i.e returns a dict).

        Arguments:
            library_name (str): The name of this library.
            payload (dict): The payload send by the `createRequestDataUpdateAction()` front-end function.
            var_name (str): The name of the variable holding the data.
            value (any): The current value of the variable identified by *var_name*.
        """
        return None

    def on_init(self, gui: "Gui") -> t.Optional[t.Tuple[str, t.Any]]:
        """
        Initialize this element library.

        This method is invoked by `Gui.run()^`.

        It allows to define variables that are accessible from elements
        defined in this element library.

        Arguments
            gui: The `Gui^` instance.

        Returns:
            An optional tuple composed of a variable name (that *must* be a valid Python
            identifier), associated with its value.<br/>
            This name can be used as the name of a variable accessible by the elements defined
            in this library.<br/>
            This name must be unique across the entire application, which is a problem since
            different element libraries might use the same symbol. A good development practice
            is to make this variable name unique by prefixing it with the name of the element
            library itself.
        """
        return None

    def on_user_init(self, state: "State"):  # noqa: B027
        """
        Initialize user state on first access.

        Arguments
            state: The `State^` instance.
        """
        pass

    def get_query(self, name: str) -> str:
        """
        Return an URL query depending on the resource name.<br/>
        Default implementation returns the version if defined.

        Arguments:
            name (str): The name of the resource for which a query should be returned.

        Returns:
            A string that holds the query part of an URL (starting with ?).
        """
        if version := self.get_version():
            return f"?{urlencode({'v': version})}"
        return ""

    def get_version(self) -> t.Optional[str]:
        """
        The optional library version

        Returns:
            An optional string representing the library version.<br/>
            This version will be appended to the resource URL as a query arg (?v=<version>)
        """
        return None
