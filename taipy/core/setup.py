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

from setuptools import find_namespace_packages, find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.json")
with open(version_path) as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [
    "networkx>=2.6,<3.0",
    "openpyxl>=3.1.2,<3.2",
    "pandas>=1.3.5,<3.0",
    "sqlalchemy>=2.0.16,<2.1",
    "toml>=0.10,<0.11",
    "taipy-config@git+https://git@github.com/Avaiga/taipy-config.git@develop",
]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "mssql": ["pyodbc>=4,<4.1"],
    "mysql": ["pymysql>1,<1.1"],
    "postgresql": ["psycopg2>2.9,<2.10"],
    "parquet": ["fastparquet==2022.11.0", "pyarrow>=14.0.2,<15.0"],
    "s3": ["boto3==1.29.1"],
    "mongo": ["pymongo[srv]>=4.2.0,<5.0"],
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
        "Programming Language :: Python :: 3.12",
    ],
    description="A Python library to build powerful and customized data-driven back-end applications.",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="taipy-core",
    name="taipy-core",
    packages=find_namespace_packages(where=".") + find_packages(include=["taipy", "taipy.core", "taipy.core.*"]),
    include_package_data=True,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-core",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
)
