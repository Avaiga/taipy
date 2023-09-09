# generate gui.pyi file
import os, json
import typing as t

os.system("pipenv run stubgen ./src/taipy/gui/gui.py --no-import --parse-only --export-less -o ./")

from src.taipy.gui.config import Config

gui_config = "".join(
    f", {k}: {v.__name__} = ..."
    if "<class" in str(v)
    else f", {k}: {str(v).replace('typing', 't').replace('src.taipy.gui.config.', '')} = ..."
    for k, v in Config.__annotations__.items()
)

replaced_content = ""
with open("./src/taipy/gui/gui.pyi", "r") as file:
    for line in file:
        if "def run(" in line:
            line = line.replace(
                ", run_server: bool = ..., run_in_thread: bool = ..., async_mode: str = ..., **kwargs", gui_config
            )
        replaced_content = replaced_content + line

with open("./src/taipy/gui/gui.pyi", "w") as write_file:
    write_file.write(replaced_content)

# Generate class api pyi file (__init__.pyi)
with open("./src/taipy/gui/viselements.json", "r") as file:
    viselements = json.load(file)
with open("./tools/class_api_templates/block.txt", "r") as file:
    block_template = file.read()
with open("./tools/class_api_templates/control.txt", "r") as file:
    control_template = file.read()

os.system("pipenv run stubgen ./src/taipy/gui/builder/__init__.py --no-import --parse-only --export-less -o ./")


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


def build_doc(element: t.Dict[str, t.Any]):
    if "doc" not in element:
        return ""
    doc = str(element["doc"]).replace("\n", f'\n{16*" "}')
    return f"{element['name']} ({element['type']}): {doc} {'(default: '+element['default_value'] + ')' if 'default_value' in element else ''}"


for control_element in viselements["controls"]:
    name = control_element[0]
    property_list = []
    property_names = []
    for property in get_properties(control_element[1], viselements):
        if property["name"] not in property_names and "[" not in property["name"]:
            property_list.append(property)
            property_names.append(property["name"])
    properties = ", ".join([f"{p} = ..." for p in property_names])
    doc_arguments = f"\n{12*' '}".join([build_doc(p) for p in property_list])
    # append properties to __init__.pyi
    with open("./src/taipy/gui/builder/__init__.pyi", "a") as file:
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
    doc_arguments = f"{8*' '}".join([build_doc(p) for p in property_list])
    # append properties to __init__.pyi
    with open("./src/taipy/gui/builder/__init__.pyi", "a") as file:
        file.write(
            block_template.replace("{{name}}", name)
            .replace("{{properties}}", properties)
            .replace("{{doc_arguments}}", doc_arguments)
        )

os.system("pipenv run isort src/taipy/gui/*.pyi")
os.system("pipenv run black src/taipy/gui/*.pyi")
os.system("pipenv run isort src/taipy/gui/builder/*.pyi")
os.system("pipenv run black src/taipy/gui/builder/*.pyi")
