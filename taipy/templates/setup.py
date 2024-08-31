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

import json
import os
from setuptools import find_namespace_packages, find_packages, setup

with open("README.md", "rb") as readme_file:
    readme = readme_file.read().decode("UTF-8")

version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.json")
with open(version_path) as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

test_requirements = ["pytest>=3.8"]

setup(
    packages=find_namespace_packages(where=".") + find_packages(include=["taipy"]),
    include_package_data=True,
    data_files=[('version', ['version.json'])],
    test_suite="tests",
    version=version_string,
)
