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

requirements = ["toml>=0.10,<0.11", "deepdiff>=6.2,<6.3"]

test_requirements = ["pytest>=3.8"]

setup(
    version=version_string,
    install_requires=requirements,
    packages=find_namespace_packages(where=".")+ find_packages(
        include=[
            "taipy",
            "taipy.common",
            "taipy.common.*",
            "taipy.common.config",
            "taipy.common.config.*",
            "taipy.common.logger",
            "taipy.common.logger.*",
            "taipy.common._cli",
            "taipy.common._cli.*"
        ]
    ),
    include_package_data=True,
    data_files=[('version', ['version.json'])],
    tests_require=test_requirements,
)
