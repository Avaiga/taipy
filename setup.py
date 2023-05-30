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
import json
import os

from setuptools import find_namespace_packages, find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open(f"src{os.sep}taipy{os.sep}rest{os.sep}version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

setup(
    author="Avaiga",
    name="taipy-rest",
    keywords="taipy-rest",
    python_requires=">=3.8",
    version=version_string,
    author_email="dev@taipy.io",
    packages=find_namespace_packages(where="src") + find_packages(include=["taipy", "taipy.rest"]),
    package_dir={"": "src"},
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
    install_requires=[
        "flask>=2.2,<2.3",
        "flask-restful>=0.3.9,<0.4",
        "flask-migrate>=3.1,<4.0",
        "flask-jwt-extended>=4.3,<5.0",
        "flask-marshmallow>=0.14,<0.15",
        "marshmallow-sqlalchemy>=0.25,<0.29",
        "passlib>=1.7.4,<1.8",
        "apispec[yaml]>=5.1,<6.0",
        "apispec-webframeworks>=0.5.2,<0.6",
        "taipy-core@git+https://git@github.com/Avaiga/taipy-core.git@develop",
    ],
)
