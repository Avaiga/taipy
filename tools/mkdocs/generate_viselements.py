# ------------------------------------------------------------------------
# generate_viselements.py
#   Generates the Markdown files for all visual elements.
#   Updates the Table of Contents for both the controls and the blocks
#     document pages.
#
# For each visual element, this script combines its property list and core
# documentation (located in [VELEMENTS_SOURCE_PATH]), and generates full
# Markdown files in [VELEMENTS_DIR_PATH]. All these files ultimately get
# integrated in the global dos set.
#
# The skeleton documentation files [GUI_DOC_PATH]/user_[controls|blocks].md_template
# are also completed with generated table of contents.
# ------------------------------------------------------------------------
import os
import warnings
import re
import shutil
import pandas as pd
import math

# Assuming that this script is located in TaipyHome/tools/mkdocs
taipy_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

GUI_DOC_PATH = taipy_dir + "/docs/manuals/gui/"
VELEMENTS_DIR_PATH = taipy_dir + "/docs/manuals/gui/viselements"
VELEMENTS_SOURCE_PATH = taipy_dir + "/gui/doc"

if not os.path.isdir(VELEMENTS_SOURCE_PATH):
    raise SystemExit(f"Error: controls documentation has not been generated {VELEMENTS_SOURCE_PATH}")


def read_skeleton(name):
    content = ""
    with open(os.path.join(GUI_DOC_PATH, "user_" + name + ".md_template")) as skeleton_file:
        content = skeleton_file.read()
    if not content:
        raise SystemExit(f"Error: could not read {name} markdown template")
    return content


controls_md_template = read_skeleton("controls")
blocks_md_template = read_skeleton("blocks")

controls_list = ["text", "button", "input", "number", "slider", "toggle", "date_selector", "chart", "file_download", "file_selector", "image",
                 "indicator", "menu", "navbar", "selector", "status", "table", "dialog", "tree"]
blocks_list = ["part", "expandable", "layout", "pane"]
# -----------------------------------------------------------------------------
# Read all element properties, including parent elements that are not
# actual visual elements (shared, lovComp...)
# -----------------------------------------------------------------------------
element_properties = {}
element_documentation = {}

for current_file in os.listdir(VELEMENTS_SOURCE_PATH):
    def read_properties(path_name, element_name):
        df = pd.read_csv(path_name, encoding='utf-8')
        properties = []
        # Row fields: name, type, default_value, doc
        for row in list(df.to_records(index=False)):
            if row[0][0] == ">":  # Inherits?
                parent = row[0][1:]
                parent_props = element_properties.get(parent)
                if parent_props is None:
                    parent_file = parent + ".csv"
                    parent_path_name = os.path.join(VELEMENTS_SOURCE_PATH, parent_file)
                    if not os.path.exists(parent_path_name):
                        raise ValueError(f"No csv file for '{parent}', inherited by '{element_name}'")
                    parent_props = read_properties(parent_path_name, parent)
                properties += parent_props
            else:
                properties.append(row)
        default_property_name = None
        for i, props in enumerate(properties):
            # Check if multiple default properties
            if props[0][0] == "*":  # Default property?
                name = props[0][1:]
                if default_property_name and name != default_property_name:
                    warnings.warn(
                        f"Property '{name}' in '{element_name}': default property already defined as {default_property_name}")
                default_property_name = name
            # Fix Boolean default property values
            if str(props[2]).lower() == "false":
                props = (props[0], props[1], "False", props[3])
                properties[i] = props
            elif str(props[2]).lower() == "true":
                props = (props[0], props[1], "True", props[3])
                properties[i] = props
            elif str(props[2]) == "nan":  # Empty cell in CSV - Pandas parsing?
                props = (props[0], props[1], "<i>Mandatory</i>", props[3])
                properties[i] = props
            # Drop inherited properties
            if props[1] == ">":  # Inherited property?
                try:
                    inherited_prop_index = [p[0] for p in properties[i + 1:]].index(props[0])
                    properties[i] = properties[i + 1 + inherited_prop_index]
                    properties.pop(i + 1 + inherited_prop_index)
                except:
                    raise ValueError(f"No inherited property '{props[0]}' in element '{element_name}'")
        if not default_property_name and (element_name in controls_list + blocks_list):
            raise ValueError(f"Element '{element_name}' has no defined default property")
        element_properties[element_name] = properties
        return properties

    element_name = os.path.basename(current_file)
    if not element_name in element_properties:
        path_name = os.path.join(VELEMENTS_SOURCE_PATH, current_file)
        element_name, current_file_ext = os.path.splitext(element_name)
        if current_file_ext == ".csv":
            read_properties(path_name, element_name)
        elif current_file_ext == ".md":
            with open(path_name, "r") as doc_file:
                element_documentation[element_name] = doc_file.read()

# Create VELEMENTS_DIR_PATH directory if necessary
if not os.path.exists(VELEMENTS_DIR_PATH):
    os.mkdir(VELEMENTS_DIR_PATH)

FIRST_PARA_RE = re.compile(r"(^.*?)(:?\n\n)", re.MULTILINE | re.DOTALL)
FIRST_HEADER2_RE = re.compile(r"(^.*?)(\n##\s+)", re.MULTILINE | re.DOTALL)


def generate_element_doc(element_name: str, toc):
    """
    Returns the entry for the Table of Contents that is inserted
    in the global Visual Elements doc page.
    """
    properties = element_properties[element_name]
    documentation = element_documentation[element_name]
    # Retrieve first paragraph from element documentation
    match = FIRST_PARA_RE.match(documentation)
    if not match:
        raise ValueError(f"Couldn't locate first paragraph in documentation for element '{element_name}'")
    first_documentation_paragraph = match.group(1)

    # Build properties table
    properties_table = """
## Properties\n\n
<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
"""
    STAR = "(&#9733;)"
    default_property_name = None
    for name, type, default_value, doc in properties:
        if name[0] == "*":
            default_property_name = name[1:]
            full_name = f"<code id=\"p-{default_property_name}\"><u><bold>{default_property_name}</bold></u></code><sup><a href=\"#dv\">{STAR}</a></sup>"
        else:
            full_name = f"<code id=\"p-{name}\">{name}</code>"
        properties_table += ("<tr>\n"
                             + f"<td nowrap>{full_name}</td>\n"
                             + f"<td>{type}</td>\n"
                             + f"<td nowrap>{default_value}</td>\n"
                             + f"<td><p>{doc}</p></td>\n"
                             + "</tr>\n")
    properties_table += "  </tbody>\n</table>\n\n"
    if default_property_name:
        properties_table += (f"<p><sup id=\"dv\">{STAR}</sup>"
                             + f"<a href=\"#p-{default_property_name}\" title=\"Jump to the default property documentation.\">"
                             + f"<code>{default_property_name}</code></a>"
                             + " is the default property for this visual element.</p>\n")

    # Insert title and properties in element documentation
    match = FIRST_HEADER2_RE.match(documentation)
    if not match:
        raise ValueError(f"Couldn't locate first header2 in documentation for element '{element_name}'")
    output_path = os.path.join(VELEMENTS_DIR_PATH, element_name + ".md")
    with open(output_path, "w") as output_file:
        output_file.write(f"# `{element_name}`\n\n"
                          + match.group(1)
                          + properties_table
                          + match.group(2) + documentation[match.end():])
    e = element_name  # Shortcut
    return (f"<a class=\"tp-ve-card\" href=\"../viselements/{e}/\">\n"
            + f"<div>{e}</div>\n"
            + f"<img class=\"tp-ve-l\" src=\"/assets/images/gui-ve/{e}-l.png\"/>\n"
            + f"<img class=\"tp-ve-lh\" src=\"/assets/images/gui-ve/{e}-lh.png\"/>\n"
            + f"<img class=\"tp-ve-d\" src=\"/assets/images/gui-ve/{e}-d.png\"/>\n"
            + f"<img class=\"tp-ve-dh\" src=\"/assets/images/gui-ve/{e}-dh.png\"/>\n"
            + f"<p>{first_documentation_paragraph}</p>\n"
            + "</a>\n")
    # If you want a simple list, use
    # f"<li><a href=\"../viselements/{e}/\"><code>{e}</code></a>: {first_documentation_paragraph}</li>\n"
    # The toc header and footer must then be "<ui>" and "</ul>" respectively.


# Generate controls doc page
toc = "<div class=\"tp-ve-cards\">\n"
for name in controls_list:
    toc += generate_element_doc(name, toc)
toc += "</div>\n"
with open(os.path.join(GUI_DOC_PATH, "user_controls.md"), "w") as file:
    file.write(controls_md_template.replace("[TOC]", toc))

# Generate blocks doc page
toc = "<div class=\"tp-ve-cards\">\n"
for name in blocks_list:
    toc += generate_element_doc(name, toc)
toc += "</div>\n"
with open(os.path.join(GUI_DOC_PATH, "user_blocks.md"), "w") as file:
    file.write(blocks_md_template.replace("[TOC]", toc))
