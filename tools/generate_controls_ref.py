# ------------------------------------------------------------------------
# generate_controls_ref.py
#   Generates the home page for Taipy controls documentation.
#
# The documentation for Taipy controls is generated using
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

SKELETON_PATH = "../docs/gui/controls.md_template"
CONTROLS_MD_PATH = "../docs/gui/controls.md"
CONTROLS_DIR_PATH = "../docs/gui/controls"
CONTROLS_DOC_PATH = "../gui/generateddoc"

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
    if os.path.isfile(current):
        with open(current, "r") as control_file:
            control_text = control_file.read()
            match = TITLE_RE.match(control_text)
            if match:
                control_type = match.group(1)
                short_desc = ""
                para_end_match = FIRST_PARA_END_RE.match(control_text[match.end():])
                if para_end_match:
                    short_desc = ": " + para_end_match.group(1)
                    short_desc = MD_REF_IN_DESC.sub(r"[`\1`](\1/)", short_desc)
                controls_list += f" - [`{control_type}`](controls/{control_type}.md){short_desc}\n"
        # Copy md file to CONTROLS_DIR_PATH
        shutil.copy(current, CONTROLS_DIR_PATH)

with open(CONTROLS_MD_PATH, "w") as controls_file:
    output_data = skeleton_data.replace("[CONTROLS_LIST]", controls_list)
    controls_file.write(output_data)
