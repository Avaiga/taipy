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
import os
from pathlib import Path

from setuptools import find_namespace_packages, find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

readme = Path("README.md").read_text()

version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.json")
with open(version_path) as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"


def get_requirements():
    # get requirements from the different setups in tools/packages (removing taipy packages)
    reqs = set()
    for pkg in (root_folder / "tools" / "packages").iterdir():
        requirements_file = pkg / "setup.requirements.txt"
        if requirements_file.exists():
            reqs.update(requirements_file.read_text("UTF-8").splitlines())

    return [r for r in reqs if r and not r.startswith("taipy")]


test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "arrow": ["pyarrow>=14.0.2,<15.0"],
}


def _build_webapp():
    already_exists = Path("./taipy/gui/webapp/index.html").exists()
    if not already_exists:
        os.system("cd ../../frontend/taipy-gui/dom && npm ci")
        os.system("cd ../../frontend/taipy-gui && npm ci --omit=optional && npm run build")


class NPMInstall(build_py):
    def run(self):
        _build_webapp()
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
        "Programming Language :: Python :: 3.12",
    ],
    description="Low-code library to create graphical user interfaces on the Web for your Python applications.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=get_requirements(),
    license="Apache License 2.0",
    include_package_data=True,
    data_files=[("version", ["version.json"])],
    keywords="taipy-gui",
    name="taipy-gui",
    packages=find_namespace_packages(where=".") + find_packages(include=["taipy", "taipy.gui", "taipy.gui.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-gui",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
