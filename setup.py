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

from setuptools import find_packages, setup, find_namespace_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "toml>=0.10,<0.11",
]

test_requirements = ["pytest>=3.8"]

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
    ],
    description="A Taipy package dedicated to easily configure a Taipy application.",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="taipy-config",
    name="taipy-config",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src") + find_packages(include=["taipy", "taipy.config", "taipy.config.*", "taipy.logger", "taipy.logger.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-config",
    version="2.0.0",
    zip_safe=False,
)
