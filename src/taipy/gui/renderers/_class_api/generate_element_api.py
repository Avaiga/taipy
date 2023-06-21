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

from .element_api import BlockElementApi, ControlElementApi


def generate_element_api():
    current_frame = inspect.currentframe()
    if current_frame is None:
        raise RuntimeError("Cannot generate Element API for the current module: No frame found.")
    if current_frame.f_back is None:
        raise RuntimeError("Cannot generate Element API for the current module: taipy-gui module not found.")
    module_name = current_frame.f_back.f_globals["__name__"]
    module = sys.modules[module_name]
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "viselements.json"))) as viselements:
        data = json.load(viselements)
        if "blocks" not in data or "controls" not in data:
            raise RuntimeError("Cannot generate Element API for the current module: Invalid viselements.json file.")
        for blockElement in data["blocks"]:
            setattr(module, blockElement[0], createBlockElement(blockElement[0]))
        for controlElement in data["controls"]:
            setattr(module, controlElement[0], createControlElement(controlElement[0]))


def createBlockElement(classname):
    return createElementApi(classname, BlockElementApi)


def createControlElement(classname):
    return createElementApi(classname, ControlElementApi)


def createElementApi(classname: str, ElementBaseClass: type[BlockElementApi | ControlElementApi]):
    return type(
        classname,
        (ElementBaseClass,),
        {
            "__init__": lambda self, **kwargs: ElementBaseClass.__init__(self, **kwargs),
            "_ELEMENT_NAME": classname,
        },
    )
