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

"""The setup script for taipy-gui package"""

import json
import os
import platform
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

package_desc = Path(root_folder / "package_desc.md").read_text("UTF-8")

version_path = "taipy/gui/version.json"

setup_requirements = Path("taipy/gui/setup.requirements.txt")

with open(version_path) as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (setup_requirements).read_text("UTF-8").splitlines() if r]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "arrow": ["pyarrow>=17.0.0,<18.0"],
}


class NPMInstall(build_py):
    def run(self):
        with_shell = platform.system() == "Windows"
        print(f"Building taipy-gui frontend bundle in {root_folder}.")
        already_exists = (root_folder / "taipy" / "gui" / "webapp" / "index.html").exists()
        if already_exists:
            print(f'Found taipy-gui frontend bundle in {root_folder  / "taipy" / "gui" / "webapp"}.')
        else:
            subprocess.run(
                ["npm", "ci"], cwd=root_folder / "frontend" / "taipy-gui" / "dom", check=True, shell=with_shell
            )
            subprocess.run(
                ["npm", "ci"], cwd=root_folder / "frontend" / "taipy-gui", check=True, shell=with_shell,
            )
            subprocess.run(
                ["npm", "run", "build"], cwd=root_folder / "frontend" / "taipy-gui", check=True, shell=with_shell
            )
        build_py.run(self)


setup(
    version=version_string,
    install_requires=requirements,
    packages=find_packages(where=root_folder, include=["taipy", "taipy.gui", "taipy.gui.*"]),
    include_package_data=True,
    data_files=[("version", [version_path])],
    tests_require=test_requirements,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
