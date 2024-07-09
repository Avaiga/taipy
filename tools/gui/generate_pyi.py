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

import json
import os
import re
import typing as t

from markdownify import markdownify

# ############################################################
# Generate Python interface definition files
# ############################################################
from taipy.gui.config import Config

# ############################################################
# Generate gui pyi file (gui/gui.pyi)
# ############################################################
gui_py_file = "./taipy/gui/gui.py"
gui_pyi_file = gui_py_file + "i"

os.system(f"pipenv run stubgen {gui_py_file} --no-import --parse-only --export-less -o ./")


gui_config = "".join(
    f", {k}: {v.__name__} = ..."
    if "<class" in str(v)
    else f", {k}: {str(v).replace('typing', 't').replace('taipy.gui.config.', '')} = ..."
    for k, v in Config.__annotations__.items()
)

replaced_content = ""
with open(gui_pyi_file, "r") as file:
    for line in file:
        if "def run(" in line:
            replace_str = line[line.index(", run_server") : (line.index("**kwargs") + len("**kwargs"))]
            # ", run_server: bool = ..., run_in_thread: bool = ..., async_mode: str = ..., **kwargs"
            line = line.replace(replace_str, gui_config)
        replaced_content = replaced_content + line

with open(gui_pyi_file, "w") as write_file:
    write_file.write(replaced_content)

# ################
# Read the version
# ################
current_version = "latest"
with open("./taipy/gui/version.json", "r") as vfile:
    version = json.load(vfile)
    if "dev" in version.get("ext", ""):
        current_version = "develop"
    else:
        current_version = f'release-{version.get("major", 0)}.{version.get("minor", 0)}'
taipy_doc_url = f"https://docs.taipy.io/en/{current_version}/manuals/gui/viselements/"


# ############################################################
# Generate Page Builder pyi file (gui/builder/__init__.pyi)
# ############################################################
builder_py_file = "./taipy/gui/builder/__init__.py"
builder_pyi_file = builder_py_file + "i"
with open("./taipy/gui/viselements.json", "r") as file:
    viselements = json.load(file)
with open("./tools/gui/builder/block.txt", "r") as file:
    block_template = file.read()
with open("./tools/gui/builder/control.txt", "r") as file:
    control_template = file.read()

os.system(f"pipenv run stubgen {builder_py_file} --no-import --parse-only --export-less -o ./")

with open(builder_pyi_file, "a") as file:
    file.write("from ._element import _Element, _Block, _Control\n")


def get_properties(element, viselements) -> t.List[t.Dict[str, t.Any]]:
    properties = element["properties"]
    if "inherits" not in element:
        return properties
    for inherit in element["inherits"]:
        inherit_element = next((e for e in viselements["undocumented"] if e[0] == inherit), None)
        if inherit_element is None:
            inherit_element = next((e for e in viselements["blocks"] if e[0] == inherit), None)
        if inherit_element is None:
            inherit_element = next((e for e in viselements["controls"] if e[0] == inherit), None)
        if inherit_element is None:
            raise RuntimeError(f"Can't find element with name {inherit}")
        properties += get_properties(inherit_element[1], viselements)
    return properties


def build_doc(name: str, element: t.Dict[str, t.Any]):
    if "doc" not in element:
        return ""
    doc = str(element["doc"]).replace("\n", f'\n{16*" "}')
    doc = re.sub(
        r"^(.*\..*\shref=\")([^h].*)(\".*\..*)$",
        r"\1" + taipy_doc_url + name + r"/\2\3",
        doc,
    )
    doc = re.sub(
        r"^(.*\.)(<br/>|\s)(See below((?!href=).)*\.)(.*)$",
        r"\1\3",
        doc,
    )
    doc = markdownify(doc, strip=["br"])
    return f"{element['name']} ({element['type']}): {doc} {'(default: '+markdownify(element['default_value']) + ')' if 'default_value' in element else ''}"  # noqa: E501


for control_element in viselements["controls"]:
    name = control_element[0]
    property_list: t.List[t.Dict[str, t.Any]] = []
    property_names: t.List[str] = []
    hidden_properties: t.List[str] = []
    for property in get_properties(control_element[1], viselements):
        if "hide" in property and property["hide"] is True:
            hidden_properties.append(property["name"])
            continue
        if (
            property["name"] not in property_names
            and "[" not in property["name"]
            and property["name"] not in hidden_properties
        ):
            if "default_property" in property and property["default_property"] is True:
                property_list.insert(0, property)
                property_names.insert(0, property["name"])
                continue
            property_list.append(property)
            property_names.append(property["name"])
    properties = ", ".join([f"{p} = ..." for p in property_names if p not in hidden_properties])
    doc_arguments = "\n".join([build_doc(name, p) for p in property_list if p["name"] not in hidden_properties])
    # append properties to __init__.pyi
    with open(builder_pyi_file, "a") as file:
        file.write(
            control_template.replace("{{name}}", name)
            .replace("{{properties}}", properties)
            .replace("{{doc_arguments}}", doc_arguments)
        )

for block_element in viselements["blocks"]:
    name = block_element[0]
    property_list = []
    property_names = []
    for property in get_properties(block_element[1], viselements):
        if property["name"] not in property_names and "[" not in property["name"]:
            property_list.append(property)
            property_names.append(property["name"])
    properties = ", ".join([f"{p} = ..." for p in property_names])
    doc_arguments = "\n".join([build_doc(name, p) for p in property_list])
    # append properties to __init__.pyi
    with open(builder_pyi_file, "a") as file:
        file.write(
            block_template.replace("{{name}}", name)
            .replace("{{properties}}", properties)
            .replace("{{doc_arguments}}", doc_arguments)
        )

os.system(f"pipenv run isort {gui_pyi_file}")
os.system(f"pipenv run black {gui_pyi_file}")
os.system(f"pipenv run isort {builder_pyi_file}")
os.system(f"pipenv run black {builder_pyi_file}")
