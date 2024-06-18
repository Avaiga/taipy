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

"""The setup script for taipy-rest package"""

import json
import os
from pathlib import Path

from setuptools import find_namespace_packages, find_packages, setup

root_folder = Path(__file__).parent

package_desc = Path("package_desc.md").read_text("UTF-8")

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
        if "taipy-rest" not in str(pkg):
            continue
        requirements_file = pkg / "setup.requirements.txt"
        if requirements_file.exists():
            reqs.update(requirements_file.read_text("UTF-8").splitlines())

    return [r for r in reqs if r and not r.startswith("taipy")]


setup(
    author="Avaiga",
    name="taipy-rest",
    keywords="taipy-rest",
    python_requires=">=3.8",
    version=version_string,
    author_email="dev@taipy.io",
    packages=find_namespace_packages(where=".") + find_packages(include=["taipy", "taipy.rest"]),
    include_package_data=True,
    data_files=[('version', ['version.json'])],
    long_description=package_desc,
    long_description_content_type="text/markdown",
    description="Library to expose taipy-core REST APIs.",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    install_requires=get_requirements(),
    project_urls={
        "Homepage": "https://www.taipy.io",
        "Documentation": "https://docs.taipy.io",
        "Source": "https://github.com/Avaiga/taipy",
        "Download": "https://pypi.org/project/taipy/#files",
        "Tracker": "https://github.com/Avaiga/taipy/issues",
        "Security": "https://github.com/Avaiga/taipy?tab=security-ov-file#readme",
        f"Release notes": "https://docs.taipy.io/en/release-{version_string}/relnotes/",
    },
)
