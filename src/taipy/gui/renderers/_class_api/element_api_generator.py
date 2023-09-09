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

import inspect
import json
import os
import sys
import types
import typing as t

from taipy.logger._taipy_logger import _TaipyLogger

from ...utils.singleton import _Singleton
from .element_api import BlockElementApi, ControlElementApi

if t.TYPE_CHECKING:
    from ...extension.library import ElementLibrary


class _ElementApiGenerator(object, metaclass=_Singleton):
    def __init__(self):
        self.__module: types.ModuleType | None = None

    def add_default(self):
        current_frame = inspect.currentframe()
        if current_frame is None:
            raise RuntimeError("Cannot generate Element API for the current module: No frame found.")
        if current_frame.f_back is None:
            raise RuntimeError("Cannot generate Element API for the current module: taipy-gui module not found.")
        module_name = current_frame.f_back.f_globals["__name__"]
        self.__module = module = sys.modules[module_name]
        with open(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "viselements.json"))
        ) as viselements:
            data = json.load(viselements)
            if "blocks" not in data or "controls" not in data:
                raise RuntimeError("Cannot generate Element API for the current module: Invalid viselements.json file.")
            for blockElement in data["blocks"]:
                setattr(
                    module, blockElement[0], _ElementApiGenerator.createBlockElement(blockElement[0], blockElement[0])
                )
            for controlElement in data["controls"]:
                setattr(
                    module,
                    controlElement[0],
                    _ElementApiGenerator.createControlElement(controlElement[0], controlElement[0]),
                )

    def add_library(self, library: "ElementLibrary"):
        library_name = library.get_name()
        if self.__module is None:
            _TaipyLogger._get_logger().info(
                "Python API for extension library '{library_name}' will not be available. To fix this, import 'taipy.gui.builder' before importing the extension library."
            )
            return
        library_module = getattr(self.__module, library_name, None)
        if library_module is None:
            library_module = types.ModuleType(library_name)
            setattr(self.__module, library_name, library_module)
        for element_name in library.get_elements().keys():
            setattr(
                library_module,
                element_name,
                _ElementApiGenerator().createControlElement(element_name, f"{library_name}.{element_name}"),
            )

    @staticmethod
    def createBlockElement(classname: str, element_name: str):
        return _ElementApiGenerator.createElementApi(classname, element_name, BlockElementApi)

    @staticmethod
    def createControlElement(classname: str, element_name: str):
        return _ElementApiGenerator.createElementApi(classname, element_name, ControlElementApi)

    @staticmethod
    def createElementApi(
        classname: str, element_name: str, ElementBaseClass: t.Union[t.Type[BlockElementApi], t.Type[ControlElementApi]]
    ):
        return type(
            classname,
            (ElementBaseClass,),
            {
                "__init__": lambda self, **kwargs: ElementBaseClass.__init__(self, **kwargs),
                "_ELEMENT_NAME": element_name,
            },
        )
