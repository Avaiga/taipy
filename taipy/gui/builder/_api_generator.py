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

import inspect
import json
import os
import sys
import types
import typing as t

from taipy.common.logger._taipy_logger import _TaipyLogger

from ..utils.singleton import _Singleton
from ..utils.viselements import VisElementProperties, VisElements, resolve_inherits
from ._element import _Block, _Control

if t.TYPE_CHECKING:
    from ..extension.library import ElementLibrary


class _ElementApiGenerator(object, metaclass=_Singleton):
    def __init__(self) -> None:
        self.__module: t.Optional[types.ModuleType] = None

    @staticmethod
    def find_default_property(property_list: t.List[VisElementProperties]) -> str:
        for property in property_list:
            if property.get("default_property", False) is True:
                return property["name"]
        return ""

    @staticmethod
    def get_properties_dict(property_list: t.List[VisElementProperties]) -> t.Dict[str, t.Any]:
        return {prop["name"]: prop.get("type", "str") for prop in property_list}

    def add_default(self):
        if self.__module is not None:
            return
        current_frame = inspect.currentframe()
        error_message = "Cannot generate elements API for the current module"
        if current_frame is None:
            raise RuntimeError(f"{error_message}: No frame found.")
        if current_frame.f_back is None:
            raise RuntimeError(f"{error_message}: taipy-gui module not found.")
        module_name = current_frame.f_back.f_globals["__name__"]
        self.__module = module = sys.modules[module_name]
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "viselements.json"))) as f:
            viselements_json = json.load(f)
            if "blocks" not in viselements_json or "controls" not in viselements_json:
                raise RuntimeError(f"{error_message}: Invalid viselements.json file.")
            viselements = resolve_inherits(t.cast(VisElements, viselements_json))
            for blockElement in viselements["blocks"]:
                default_property = _ElementApiGenerator.find_default_property(blockElement[1]["properties"])
                setattr(
                    module,
                    blockElement[0],
                    _ElementApiGenerator.create_block_api(
                        blockElement[0],
                        blockElement[0],
                        default_property,
                        _ElementApiGenerator.get_properties_dict(blockElement[1]["properties"]),
                    ),
                )
            for controlElement in viselements["controls"]:
                default_property = _ElementApiGenerator.find_default_property(controlElement[1]["properties"])
                setattr(
                    module,
                    controlElement[0],
                    _ElementApiGenerator.create_control_api(
                        controlElement[0],
                        controlElement[0],
                        default_property,
                        _ElementApiGenerator.get_properties_dict(controlElement[1]["properties"]),
                    ),
                )

    def add_library(self, library: "ElementLibrary"):
        library_name = library.get_name()
        if self.__module is None:
            _TaipyLogger._get_logger().info(
                f"Python API for extension library '{library_name}' is not available. To fix this, import 'taipy.gui.builder' before importing the extension library."  # noqa: E501
            )
            return
        library_module = getattr(self.__module, library_name, None)
        if library_module is None:
            library_module = types.ModuleType(library_name)
            setattr(self.__module, library_name, library_module)
        for element_name, element in library.get_elements().items():
            setattr(
                library_module,
                element_name,
                _ElementApiGenerator().create_control_api(
                    element_name,
                    f"{library_name}.{element_name}",
                    element.default_attribute,
                    {name: str(prop.property_type) for name, prop in element.attributes.items()},
                ),
            )
            # Allow element to be accessed from the root module
            if hasattr(self.__module, element_name):
                _TaipyLogger._get_logger().info(
                    f"Can't add element `{element_name}` of library `{library_name}` to the root of Builder API as another element with the same name already exists."  # noqa: E501
                )
                continue
            setattr(self.__module, element_name, getattr(library_module, element_name))

    @staticmethod
    def create_block_api(
        classname: str,
        element_name: str,
        default_property: str,
        properties: t.Dict[str, str],
    ):
        return _ElementApiGenerator.create_element_api(classname, element_name, default_property, properties, _Block)

    @staticmethod
    def create_control_api(
        classname: str,
        element_name: str,
        default_property: str,
        properties: t.Dict[str, str],
    ):
        return _ElementApiGenerator.create_element_api(classname, element_name, default_property, properties, _Control)

    @staticmethod
    def create_element_api(
        classname: str,
        element_name: str,
        default_property: str,
        properties: t.Dict[str, str],
        ElementBaseClass: t.Union[t.Type[_Block], t.Type[_Control]],
    ):
        return type(
            classname,
            (ElementBaseClass,),
            {
                "_ELEMENT_NAME": element_name,
                "_DEFAULT_PROPERTY": default_property,
                "_TYPES": {f"{parts[0]}__" if len(parts := k.split("[")) > 1 else k: v for k, v in properties.items()},
            },
        )
