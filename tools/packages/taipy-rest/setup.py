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

from pathlib import Path

from setuptools import find_packages, setup

root_folder = Path(__file__).parent

readme = Path(root_folder / "README.md").read_text("UTF-8")

with open(root_folder / "taipy" / "rest" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (root_folder / "setup.requirements.txt").read_text("UTF-8").splitlines() if r]

setup(
    author="Avaiga",
    name="taipy-rest",
    keywords="taipy-rest",
    python_requires=">=3.8",
    version=version_string,
    author_email="dev@taipy.io",
    packages=find_packages(where=root_folder, include=["taipy", "taipy.rest", "taipy.rest.*"]),
    include_package_data=True,
    long_description=readme,
    long_description_content_type="text/markdown",
    description="Library to expose taipy-core REST APIs.",
    license="Apache License 2.0",
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
    install_requires=requirements,
)
