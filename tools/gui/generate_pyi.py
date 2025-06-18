# Copyright 2021-2025 Avaiga Private Limited
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
import sys
from typing import Any, Dict, List, Union, get_args, get_origin

from markdownify import markdownify

__RE_INDEXED_PROPERTY = re.compile(r"^([\w_]+)\[(<\w+>)?([\w]+)(</\w+>)?\]$")

# Script should be located in <taipy_root>/tools
script_dir = os.path.dirname(os.path.realpath(__file__))
# Move to <taipy_root>
root_dir = os.path.dirname(os.path.dirname(script_dir))
os.chdir(root_dir)
# Make sure we can import the mandatory packages
if not os.path.isdir(os.path.abspath(os.path.join(script_dir, "taipy"))):
    sys.path.append(os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir)))

# Classes package
classes_xrefs = {
    "Cycle": "core",
    "DataNode": "core",
    "Job": "core",
    "Scenario": "core",
    "Sequence": "core",
    "State": "gui",
}
# Read package version - Point to 'develop' branch if 'ext' is not null
reference_url = "https://docs.taipy.io/en/[BRANCH]/refmans/reference/pkg_taipy/"
with open(os.path.join(os.path.join(root_dir, "taipy", "version.json"))) as version_file:
    version = json.load(version_file)
    branch = "develop"
    if not version.get("ext"):
        branch = f"release-{version.get('major', 0)}.{version.get('minor', 0)}"
    reference_url = reference_url.replace("[BRANCH]", branch)

# ##################################################################################################
# Generate gui pyi file (gui/gui.pyi)
# ##################################################################################################
gui_py_file = "./taipy/gui/gui.py"
gui_pyi_file = f"{gui_py_file}i"
from taipy.gui.config import Config  # noqa: E402

# Generate Python interface definition files
os.system(f"pipenv run stubgen {gui_py_file} --no-import --parse-only --export-less -o ./")

gui_config = "".join(
    (
        f", {k}: {v.__name__} = ..."
        if "<class" in str(v)
        else f", {k}: {str(v).replace('typing', 't').replace('taipy.gui.config.', '')} = ..."
    )
    for k, v in Config.__annotations__.items()
)

replaced_content = ""
with open(gui_pyi_file, "r", encoding="utf-8") as file:
    for line in file:
        if "def run(" in line:
            replace_str = line[line.index(", run_server") : (line.index("**kwargs") + len("**kwargs"))]
            # ", run_server: bool = ..., run_in_thread: bool = ..., async_mode: str = ..., **kwargs"
            line = line.replace(replace_str, gui_config)
        replaced_content += line

with open(gui_pyi_file, "w", encoding="utf-8") as write_file:
    write_file.write(replaced_content)

# ##################################################################################################
# Generate Page Builder pyi file (gui/builder/__init__.pyi)
# ##################################################################################################
# Types that appear in viselements.json

from datetime import datetime  # noqa: E402, F401

from taipy.core import Cycle, DataNode, Job, Scenario  # noqa: E402, F401
from taipy.gui import Icon  # noqa: E402, F401

# Read the version
current_version = "latest"
with open("./taipy/gui/version.json", "r", encoding="utf-8") as vfile:
    version = json.load(vfile)
    if "dev" in version.get("ext", ""):
        current_version = "develop"
    else:
        current_version = f'release-{version.get("major", 0)}.{version.get("minor", 0)}'

taipy_doc_url = f"https://docs.taipy.io/en/{current_version}/manuals/userman/gui/viselements/generic/"

builder_py_file = "./taipy/gui/builder/__init__.py"
builder_pyi_file = f"{builder_py_file}i"
controls: Dict[str, List] = {}
blocks: Dict[str, List] = {}
undocumented: Dict[str, List] = {}
with open("./taipy/gui/viselements.json", "r", encoding="utf-8") as file:
    viselements: Dict[str, List] = json.load(file)
    controls[""] = viselements.get("controls", [])
    blocks[""] = viselements.get("blocks", [])
    undocumented[""] = viselements.get("undocumented", [])
with open("./taipy/gui_core/viselements.json", "r", encoding="utf-8") as file:
    core_viselements: Dict[str, List] = json.load(file)
    controls["core"] = core_viselements.get("controls", [])
    blocks["core"] = core_viselements.get("blocks", [])
    undocumented["core"] = core_viselements.get("undocumented", [])

os.system(f"pipenv run stubgen {builder_py_file} --no-import --parse-only --export-less -o ./")

with open(builder_pyi_file, "a", encoding="utf-8") as file:
    file.write("from datetime import datetime\n")
    file.write("from importlib.util import find_spec\n")
    file.write("from typing import Any, Callable, Optional, Union\n")
    file.write("\n")
    file.write("from .. import Icon\n")
    file.write("from ._element import _Block, _Control\n")
    file.write('if find_spec("taipy.core"):\n')
    file.write("\tfrom taipy.core import Cycle, DataNode, Job, Scenario\n")


def resolve_inherit(
    name: str, properties, inherits, blocks: List, controls: List, undocumented: List
) -> List[Dict[str, Any]]:
    if not inherits:
        return properties
    for inherit_name in inherits:
        inherited_desc = next((e for e in undocumented if e[0] == inherit_name), None)
        if inherited_desc is None:
            inherited_desc = next((e for e in blocks if e[0] == inherit_name), None)
        if inherited_desc is None:
            inherited_desc = next((e for e in controls if e[0] == inherit_name), None)
        if inherited_desc is None:
            raise RuntimeError(f"Element type '{name}' inherits from unknown element type '{inherit_name}'")
        inherited_desc = inherited_desc[1]
        for inherit_prop in inherited_desc["properties"]:
            prop_desc = next((p for p in properties if p["name"] == inherit_prop["name"]), None)
            if prop_desc:  # Property exists

                def override(current, inherits, p: str):
                    if p not in current and (inherited := inherits.get(p, None)):
                        current[p] = inherited

                override(prop_desc, inherit_prop, "type")
                override(prop_desc, inherit_prop, "default_value")
                override(prop_desc, inherit_prop, "doc")
                override(prop_desc, inherit_prop, "signature")
            else:
                properties.append(inherit_prop)
            properties = resolve_inherit(
                inherit_name, properties, inherited_desc.get("inherits", None), blocks, controls, undocumented
            )
    return properties


def format_as_parameter(property: Dict[str, str], element_name: str):
    name = property["name"]
    if match := __RE_INDEXED_PROPERTY.match(name):
        name = f"{match.group(1)}__{match.group(3)}"
    type = property["type"]
    if m := re.match(r"indexed\((.*)\)", type):
        type = m[1]
        property["indexed"] = " (indexed)"
    else:
        property["indexed"] = ""
    if m := re.match(r"dynamic\((.*)\)", type):
        type = m[1]
        property["dynamic"] = " (dynamic)"
    else:
        property["dynamic"] = ""
    default_value = property.get("default_value", None)
    type, _ = re.subn(r"\bCallable|Callback|Function\b", "callable", type)
    type = re.sub(r"((plotly|taipy)\.[\w\.]*)", r'"\1"', type)
    try:
        type_desc = eval(type)
        if get_origin(type_desc) is Union:
            types = get_args(type_desc)
            if not any(t.__name__ in ["str", "Any"] for t in types):
                type = type.rpartition("]")[0]
                type = type + ", str]"
        elif hasattr(type_desc, "__name__") and type_desc.__name__ not in ["str", "Any"]:
            type = f"Union[{type}, str]"
    except NameError:
        print(f"WARNING - Couldn't parse type '{type}' in {element_name}.{name}")  # noqa: T201

    if default_value is None or default_value == "None":
        default_value = " = None"
        if type.startswith("Union["):
            type = type.rpartition("]")[0]
            type = ": " + type + ", None]"
        else:
            type = f": Optional[{type}]"
    else:
        try:
            eval(default_value)
            default_value = f" = {default_value}"
            if type:
                type = f": {type}"
        except Exception:
            default_value = " = None"
            if type.startswith("Union["):
                type = type.rpartition("]")
                type = ": " + type[0] + ", None]"
            else:
                type = f": Optional[{type}]"
    return f"{name}{type}{default_value}"


def replace_ref_xref(match: re.Match) -> str:
    if package := classes_xrefs.get(match[1]):
        return (
            '<a href="'
            + reference_url
            + "/".join([f"pkg_{p}" for p in package.split(".")])
            + f'/{match[1]}/">'
            + match[1]
            + "</a>"
        )
    else:
        return match[0]


def build_doc(name: str, desc: Dict[str, Any]):
    if "doc" not in desc:
        return ""
    doc = str(desc["doc"])
    # Hack to replace the actual element name in the class_name property doc
    if desc["name"] == "class_name":
        doc = doc.replace("[element_type]", name)
    # This won't work for Scenario Management and Block elements
    doc = re.sub(r"(href=\")\.\.((?:.*?)\")", r"\1" + taipy_doc_url + name + r"/../..\2", doc)
    doc = re.sub(r"<tt>([\w_]+)</tt>", r"`\1`", doc)  # <tt> not processed properly by markdownify()
    doc = "\n  ".join(markdownify(doc).split("\n"))
    # <, >, `, [, -, _ and * prefixed with a \
    doc = doc.replace("  \n", "  \\n").replace("\\<", "<").replace("\\>", ">").replace("\\`", "`")
    doc = doc.replace("\\[", "[").replace("\\-", "-").replace("\\_", "_").replace("\\*", "*")
    # Final dots are prefixed with a \
    doc = re.sub(r"\\.$", ".", doc)
    # Link anchors # signs are prefixed with a \
    doc = re.sub(r"\\(#[a-z_]+\))", r"\1", doc)
    doc = re.sub(r"(?:\s+\\n)?\s+See below(?:[^\.]*)?\.", "", doc).replace("\n", "\\n")
    # External links
    doc = re.sub(r"`(\w+)\^`", replace_ref_xref, doc)
    return f"{desc['name']}{desc['dynamic']}{desc['indexed']}\\n  {doc}\\n\\n"


def element_template(name: str, base_class: str, n: str, properties_decl: str, properties_doc: str, ind: str):
    return f"""

{ind}class {name}(_{base_class}):
{ind}    _ELEMENT_NAME: str
{ind}    def __init__(self, {properties_decl}) -> None:
{ind}        \"\"\"Creates a{n} {name} element.\\n\\nParameters\\n----------\\n\\n{properties_doc}\"\"\"  # noqa: E501
{ind}        ...
"""


def generate_elements(elements_by_prefix: Dict[str, List], base_class: str):
    for prefix, elements in elements_by_prefix.items():
        if not elements:
            continue
        indent = ""
        if prefix:
            indent = "    "
            with open(builder_pyi_file, "a", encoding="utf-8") as file:
                file.write(prefix + "\n")
        for element in elements:
            name = element[0]
            desc = element[1]
            properties_doc = ""
            property_list: List[Dict[str, Any]] = []
            property_indices: List[int] = []
            properties = resolve_inherit(
                name,
                desc["properties"],
                desc.get("inherits", None),
                blocks.get(prefix, []),
                controls.get(prefix, []),
                undocumented.get(prefix, []),
            )
            # Remove hidden properties
            properties = [p for p in properties if not p.get("hide", False)]
            # Generate function parameters (modifies properties!)
            properties_decl = [format_as_parameter(p, name) for p in properties]
            # Generate properties doc
            for idx, property in enumerate(properties):
                if "default_property" in property and property["default_property"] is True:
                    property_list.insert(0, property)
                    property_indices.insert(0, idx)
                    continue
                property_list.append(property)
                property_indices.append(idx)
            # Append properties doc to element doc
            for property in property_list:
                property_doc = build_doc(name, property)
                properties_doc += property_doc
            # Sort properties by indices
            properties_decl = [properties_decl[idx] for idx in property_indices]
            if name == "text":
                properties_doc += (
                    "inline\n  If True, the text is created next to "
                    + "the previous element and not on a new line.\n\n"
                )
                # Manually add the 'inline' property for the text control
                properties_decl.append("inline: bool = False")
            if len(properties_decl) > 1:
                properties_decl.insert(1, "*")
            # Append element to __init__.pyi
            with open(builder_pyi_file, "a", encoding="utf-8") as file:
                file.write(
                    element_template(
                        name,
                        base_class,
                        "n" if name[0] in ["a", "e", "i", "o"] else "",
                        ", ".join(properties_decl),
                        properties_doc,
                        indent,
                    )
                )


generate_elements(controls, "Control")
generate_elements(blocks, "Block")

os.system(f"pipenv run isort {gui_pyi_file}")
os.system(f"pipenv run black {gui_pyi_file}")
os.system(f"pipenv run isort {builder_pyi_file}")
os.system(f"pipenv run black {builder_pyi_file}")
