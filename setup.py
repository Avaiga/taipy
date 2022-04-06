#!/usr/bin/env python

# Copyright 2022 Avaiga Private Limited
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

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "networkx",
    "numpy",
    "openpyxl",
    "pandas",
    "simple-websocket",
    "sqlalchemy",
    "toml",
]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "mssql": ["pyodbc>=4"],
}

setup(
    author="Avaiga",
    author_email="taipy.dev@avaiga.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="AI Platform for Business Applications.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    keywords="taipy-core",
    name="taipy-core",
    packages=find_packages(include=["taipy", "taipy.core", "taipy.core.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-core",
    version="1.0.0.dev",
    zip_safe=False,
    extras_require=extras_require,
)
