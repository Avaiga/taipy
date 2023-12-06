#!/usr/bin/env python

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

"""The setup script."""

import json
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent.parent.parent.parent

readme = Path(root_folder / "README.md").read_text("UTF-8")

with open(root_folder / "taipy" / "gui" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [
    "flask>=3.0.0,<3.1",
    "flask-cors>=4.0.0,<5.0",
    "flask-socketio>=5.3.6,<6.0",
    "markdown>=3.4.4,<4.0",
    "pandas>=2.0.0,<3.0",
    "python-dotenv>=1.0.0,<1.1",
    "pytz>=2021.3,<2022.2",
    "tzlocal>=3.0,<5.0",
    "backports.zoneinfo>=0.2.1,<0.3;python_version<'3.9'",
    "gevent>=23.7.0,<24.0",
    "gevent-websocket>=0.10.1,<0.11",
    "kthread>=0.2.3,<0.3",
    "taipy-config",
    "gitignore-parser>=0.1,<0.2",
    "simple-websocket>=0.10.1,<1.0",
    "twisted>=23.8.0,<24.0",
]

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
        subprocess.run(
            ["python", "bundle_build.py", "gui"], cwd=root_folder / "tools" / "frontend", check=True, shell=True
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
    package_dir={"": "../../.."},
    packages=find_packages(where=root_folder, include=["taipy", "taipy.gui", "taipy.gui.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-gui",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
