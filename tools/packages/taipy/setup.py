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

"""The setup script for taipy package"""

import json
import platform
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

package_desc = (root_folder / "package_desc.md").read_text("UTF-8")

with open(root_folder / "taipy" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (root_folder / "setup.requirements.txt").read_text("UTF-8").splitlines() if r]

test_requirements = ["pytest>=3.8"]


class NPMInstall(build_py):
    def run(self):
        subprocess.run(
            ["python", "bundle_build.py"],
            cwd=root_folder / "tools" / "frontend",
            check=True,
            shell=platform.system() == "Windows",
        )
        build_py.run(self)


setup(
    version=version_string,
    install_requires=requirements,
    packages=find_packages(include=["taipy", "taipy.*"]),
    extras_require={
        "ngrok": ["pyngrok>=5.1,<6.0"],
        "image": [
            "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
            "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
        ],
        "rdp": ["rdp>=0.8"],
        "arrow": ["pyarrow>=17.0.0,<18.0"],
        "mssql": ["pyodbc>=4"],
    },
    cmdclass={"build_py": NPMInstall},
)
