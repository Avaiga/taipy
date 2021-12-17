# ------------------------------------------------------------------------
# generate_controls_ref.py
#   Generates the home page for Taipy controls documentation.
#
# The documentation for Taipy controls must have been generated using
#            npm run doc
# from the `gui` directory.
#
# This script reads the generated files (Markdown), and generates
# the [CONTROLS_MD_PATH] file that ultimately gets integrated in the
# global dos set.
# All md files get copied to CONTROLS_DIR_PATH in order to be processed
# by mkdocs.
# ------------------------------------------------------------------------
import os
import re
import shutil

# Assuming that this script is located in TaipyHome/tools/mkdocs
taipy_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

SKELETON_PATH = taipy_dir + "/docs/gui/controls.md_template"
CONTROLS_MD_PATH = taipy_dir + "/docs/gui/controls.md"
CONTROLS_DIR_PATH = taipy_dir + "/docs/gui/controls"
CONTROLS_DOC_PATH = taipy_dir + "/gui/generateddoc"

if not os.path.isdir(CONTROLS_DOC_PATH):
    raise SystemExit(f"Error: controls documentation has not been generated {CONTROLS_DOC_PATH}")

skeleton_data = ""
with open(SKELETON_PATH) as skeleton_file:
    skeleton_data = skeleton_file.read()
if not skeleton_data:
    raise SystemExit(f"Error: could not read skeleton file {SKELETON_PATH}")

TITLE_RE = re.compile(r"^\s*#\s+(\w+)\s*\n", re.MULTILINE)
FIRST_PARA_END_RE = re.compile(r"(^.*?)(:?\n\n|</?br>)", re.MULTILINE | re.DOTALL)
MD_REF_IN_DESC = re.compile(r"\[`(\w+)`\]\(\1\.md\)", re.MULTILINE | re.DOTALL)

# Create CONTROLS_DIR_PATH directory if necessary
if not os.path.exists(CONTROLS_DIR_PATH):
    os.mkdir(CONTROLS_DIR_PATH)
controls_list = ""
for file in os.listdir(CONTROLS_DOC_PATH):
    current = os.path.join(CONTROLS_DOC_PATH, file)
    control_text = None
    if os.path.isfile(current):
        with open(current, "r") as control_file:
            control_text = control_file.read()
            match = TITLE_RE.match(control_text)
            if match:
                control_type = match.group(1)
                short_desc = ""
                para_end_match = FIRST_PARA_END_RE.match(control_text[match.end() :])
                if para_end_match:
                    short_desc = ": " + para_end_match.group(1)
                    short_desc = MD_REF_IN_DESC.sub(r"[`\1`](\1/)", short_desc)
                controls_list += f" - [`{control_type}`](controls/{control_type}.md){short_desc}\n"
            # Enlarge the 'Property' column for a better rendering
            control_text = re.sub(
                r"(##\s+Properties\s+\|\s*Property)(\s+\|)",
                "\\1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\\2",
                control_text,
            )
    # Generate output Markdown file if necessary
    if control_text:
        details_path = os.path.join(CONTROLS_DIR_PATH, file + "_details")
        details_text = None
        # Is there a _template file for this control?
        if os.path.isfile(details_path):
            with open(details_path, "r") as details_file:
                details_text = details_file.read()
        # Generate final md file to CONTROLS_DIR_PATH
        output_path = os.path.join(CONTROLS_DIR_PATH, file)
        with open(output_path, "w") as output_file:
            output_file.write(control_text)
            if details_text:
                output_file.write("\n")
                output_file.write(details_text)

with open(CONTROLS_MD_PATH, "w") as controls_file:
    output_data = skeleton_data.replace("[CONTROLS_LIST]", controls_list)
    controls_file.write(output_data)
