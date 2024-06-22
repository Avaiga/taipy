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

import os
import shutil
import subprocess


def initialize_as_git_project(project_dir: str) -> str:
    if shutil.which("git") is None:
        msg = "\nERROR: Git executable not found, skipping git initialisation"
        return msg

    try:
        subprocess.run(
            ["git", "init", "."],
            cwd=project_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        msg = f"\nInitialized Git repository in {project_dir}"

    except subprocess.CalledProcessError:
        msg = f"\nERROR: Failed to initialise Git repository in {project_dir}"

    return msg


# Use TOML config file or not
use_toml_config = "{{ cookiecutter.__use_toml_config }}".upper()
if use_toml_config == "YES" or use_toml_config == "Y":
    os.remove(os.path.join(os.getcwd(), "config", "config.py"))
    os.rename(
        os.path.join(os.getcwd(), "config", "config_with_toml.py"), os.path.join(os.getcwd(), "config", "config.py")
    )
else:
    os.remove(os.path.join(os.getcwd(), "config", "config_with_toml.py"))
    os.remove(os.path.join(os.getcwd(), "config", "config.toml"))

# Initialize the project as a git repository
git_init_message = ""
if "{{ cookiecutter.__git }}".upper() in ["YES", "Y"]:
    git_init_message = initialize_as_git_project(os.getcwd())
else:
    os.remove(os.path.join(os.getcwd(), ".gitignore"))

main_file_name = "{{cookiecutter.__main_file}}.py"
print(
    f"New Taipy application has been created at {os.path.join(os.getcwd())}"
    f"{git_init_message}"
    f"\n\nTo start the application, change directory to the newly created folder:"
    f"\n\tcd {os.path.join(os.getcwd())}"
    f"\nand run the application as follows:"
    f"\n\ttaipy run {main_file_name}"
)
