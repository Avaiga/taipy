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

from setuptools import find_packages, setup

root_folder = Path(__file__).parent.parent.parent.parent

readme = Path(root_folder / "README.md").read_text("UTF-8")

with open(root_folder / "taipy" / "core" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [
    "pyarrow>=10.0.1,<11.0",
    "networkx>=2.6,<3.0",
    "openpyxl>=3.1.2,<3.2",
    "modin[dask]>=0.23.0,<1.0",
    "pymongo[srv]>=4.2.0,<5.0",
    "sqlalchemy>=2.0.16,<2.1",
    "toml>=0.10,<0.11",
    "taipy-config",
]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "fastparquet": ["fastparquet==2022.11.0"],
    "mssql": ["pyodbc>=4,<4.1"],
    "mysql": ["pymysql>1,<1.1"],
    "postgresql": ["psycopg2>2.9,<2.10"],
}

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
    description="A Python library to build powerful and customized data-driven back-end applications.",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="taipy-core",
    name="taipy-core",
    package_dir = {"" : "../../.."},
    packages=find_packages(where=root_folder, include=["taipy", "taipy.core", "taipy.core.*"]),
    include_package_data=True,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-core",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
)
