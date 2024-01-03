#!/usr/bin/env python

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

"""The setup script."""

import json
import platform
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

readme = Path(root_folder / "README.md").read_text("UTF-8")

with open(root_folder / "taipy" / "gui" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (root_folder / "setup.requirements.txt").read_text("UTF-8").splitlines() if r]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "arrow": ["pyarrow>=10.0.1,<11.0"],
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
                ["npm", "ci", "--omit=optional"],
                cwd=root_folder / "frontend" / "taipy-gui",
                check=True,
                shell=with_shell,
            )
            subprocess.run(
                ["npm", "run", "build"], cwd=root_folder / "frontend" / "taipy-gui", check=True, shell=with_shell
            )
        build_py.run(self)


setup(
    author="Avaiga",
    author_email="dev@taipy.io",
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="Low-code library to create graphical user interfaces on the Web for your Python applications.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    license="Apache License 2.0",
    include_package_data=True,
    keywords="taipy-gui",
    name="taipy-gui",
    packages=find_packages(where=root_folder, include=["taipy", "taipy.gui", "taipy.gui.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-gui",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
