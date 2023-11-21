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

import os
import shutil

import taipy


def handle_services(use_rest, use_core):
    if use_core or use_rest:
        # Write "import taipy as tp" at the third line of the import.txt file
        with open(os.path.join(os.getcwd(), "sections", "import.txt"), "r") as import_file:
            import_lines = import_file.readlines()
            import_lines[0] = "import taipy as tp\n" + import_lines[0] + "\n"
        with open(os.path.join(os.getcwd(), "sections", "import.txt"), "w") as import_file:
            import_file.writelines(import_lines)

    # Import the necessary services
    if use_core and use_rest:
        with open(os.path.join(os.getcwd(), "sections", "import.txt"), "a") as import_file:
            import_file.write("from taipy import Core, Rest\n")
    elif use_core:
        with open(os.path.join(os.getcwd(), "sections", "import.txt"), "a") as import_file:
            import_file.write("from taipy import Core\n")
    elif use_rest:
        with open(os.path.join(os.getcwd(), "sections", "import.txt"), "a") as import_file:
            import_file.write("from taipy import Rest\n")

    # Start the Rest service
    if use_rest:
        with open(os.path.join(os.getcwd(), "sections", "main.txt"), "a") as main_file:
            main_file.write("    rest = Rest()\n")

    if use_core:
        # Create and submit the placeholder scenario
        with open(os.path.join(os.getcwd(), "sections", "main.txt"), "a") as main_file:
            main_file.write("    core = Core()\n")
            main_file.write("    core.run()\n")
            main_file.write("    # #############################################################################\n")
            main_file.write("    # PLACEHOLDER: Create and submit your scenario here                           #\n")
            main_file.write("    #                                                                             #\n")
            main_file.write("    # Example:                                                                    #\n")
            main_file.write("    # from configuration import scenario_config                                   #\n")
            main_file.write("    # scenario = tp.create_scenario(scenario_config)                              #\n")
            main_file.write("    # scenario.submit()                                                           #\n")
            main_file.write("    # Comment, remove or replace the previous lines with your own use case        #\n")
            main_file.write("    # #############################################################################\n")
    else:
        shutil.rmtree(os.path.join(os.getcwd(), "algorithms"))
        shutil.rmtree(os.path.join(os.getcwd(), "configuration"))


def handle_run_service():
    with open(os.path.join(os.getcwd(), "sections", "main.txt"), "a+") as main_file:
        main_file.seek(0)
        main_content = main_file.read()
        # Run Rest service along with the GUI service
        if "rest = Rest()" in main_content:
            main_file.write('    tp.run(gui, rest, title="{{cookiecutter.__application_title}}")\n')
        else:
            main_file.write('    gui.run(title="{{cookiecutter.__application_title}}")\n')


def handle_single_page_app():
    shutil.rmtree(os.path.join(os.getcwd(), "pages"))

    with open(os.path.join(os.getcwd(), "sections", "main.txt"), "a") as main_file:
        main_file.write("\n")
        main_file.write("    gui = Gui(page=page)\n")

    handle_run_service()

    with open(os.path.join(os.getcwd(), "sections", "page_content.txt"), "a") as page_content_file:
        page_content_file.write(
            '''
page = """
<center>
<|navbar|lov={[("home", "Homepage")]}|>
</center>

"""
'''
        )


def handle_multi_page_app(pages):
    for page_name in pages:
        os.mkdir(os.path.join(os.getcwd(), "pages", page_name))
        with open(os.path.join(os.getcwd(), "pages", "page_example", "page_example.md"), "r") as page_md_file:
            page_md_content = page_md_file.read()
        page_md_content = page_md_content.replace("Page example", page_name.replace("_", " ").title())
        with open(os.path.join(os.getcwd(), "pages", page_name, page_name + ".md"), "w") as page_md_file:
            page_md_file.write(page_md_content)

        with open(os.path.join(os.getcwd(), "pages", "page_example", "page_example.py"), "r") as page_content_file:
            page_py_content = page_content_file.read()
        page_py_content = page_py_content.replace("page_example", page_name)
        with open(os.path.join(os.getcwd(), "pages", page_name, page_name + ".py"), "w") as page_content_file:
            page_content_file.write(page_py_content)

    with open(os.path.join(os.getcwd(), "pages", "__init__.py"), "a") as page_init_file:
        for page_name in pages:
            page_init_file.write(f"from .{page_name}.{page_name} import {page_name}\n")

    shutil.rmtree(os.path.join(os.getcwd(), "pages", "page_example"))

    newline = ",\n\t"
    user_page_dict = newline.join(f'"{page_name}": {page_name}' for page_name in pages)
    page_dict = """
pages = {
    "/": root_page,
    {pages}
}
"""
    with open(os.path.join(os.getcwd(), "sections", "page_content.txt"), "a") as page_content_file:
        page_content_file.write(page_dict.replace("{pages}", user_page_dict))

    with open(os.path.join(os.getcwd(), "sections", "import.txt"), "a") as import_file:
        import_file.write("from pages import *\n")

    with open(os.path.join(os.getcwd(), "sections", "main.txt"), "a") as main_file:
        main_file.write("\n")
        main_file.write("    gui = Gui(pages=pages)\n")

    handle_run_service()


def generate_main_file():
    with open(os.path.join(os.getcwd(), "sections", "import.txt"), "r") as import_file:
        import_lines = import_file.read()
    with open(os.path.join(os.getcwd(), "sections", "page_content.txt"), "r") as page_content_file:
        page_content = page_content_file.read()
    with open(os.path.join(os.getcwd(), "sections", "main.txt"), "r") as main_file:
        main_lines = main_file.read()

    with open(os.path.join(os.getcwd(), "{{cookiecutter.__main_file}}.py"), "a") as app_main_file:
        app_main_file.write(import_lines)
        app_main_file.write("\n")
        app_main_file.write(page_content)
        app_main_file.write("\n\n")
        app_main_file.write(main_lines)


with open(os.path.join(os.getcwd(), "requirements.txt"), "a") as requirement_file:
    requirement_file.write(f"taipy=={taipy.version._get_version()}\n")

use_core = "{{ cookiecutter.__core }}".upper()
use_rest = "{{ cookiecutter.__rest }}".upper()
handle_services(use_rest in ["YES", "Y"], use_core in ["YES", "Y"])

pages = "{{ cookiecutter.__pages }}".split(" ")
# Remove empty string from pages list
pages = [page for page in pages if page != ""]
if len(pages) == 0:
    handle_single_page_app()
else:
    handle_multi_page_app(pages)

generate_main_file()

# Remove the sections folder
shutil.rmtree(os.path.join(os.getcwd(), "sections"))

main_file_name = "{{cookiecutter.__main_file}}.py"
print(
    f"New Taipy application has been created at {os.path.join(os.getcwd())}"
    f"\n\nTo start the application, change directory to the newly created folder:"
    f"\n\tcd {os.path.join(os.getcwd())}"
    f"\nand run the application as follows:"
    f"\n\ttaipy run {main_file_name}"
)
