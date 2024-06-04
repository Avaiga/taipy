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

"""The setup script for taipy-gui package"""

import json
import os
import platform
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

package_desc = Path(root_folder / "package_desc.md").read_text("UTF-8")

version_path = os.path.join(root_folder, "taipy/gui/version.json")

setup_requirements = Path("taipy/gui/setup.requirements.txt")

with open(version_path) as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (setup_requirements).read_text("UTF-8").splitlines() if r]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "arrow": ["pyarrow>=14.0.2,<15.0"],
}


class NPMInstall(build_py):
    def run(self):
        with_shell = platform.system() == "Windows"
        print(f"Building taipy-gui frontend bundle in {root_folder}.")
        already_exists = (root_folder / "taipy" / "gui" / "webapp" / "index.html").exists()
        if already_exists:
            print(f'Found taipy-gui frontend bundle in {root_folder  / "taipy" / "gui" / "webapp"}.')
        else:
            subprocess.run(
                ["npm", "ci"], cwd=root_folder / "frontend" / "taipy-gui" / "dom", check=True, shell=with_shell
            )
            subprocess.run(
                ["npm", "ci", "--omit=optional"],
                cwd=root_folder / "frontend" / "taipy-gui",
                check=True,
                shell=with_shell,
            )
            subprocess.run(
                ["npm", "run", "build"], cwd=root_folder / "frontend" / "taipy-gui", check=True, shell=with_shell
            )
        build_py.run(self)


setup(
    author="Avaiga",
    author_email="dev@taipy.io",
    python_requires=">=3.8",
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
    description="Low-code library to create graphical user interfaces on the Web for your Python applications.",
    long_description=package_desc,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    license="Apache License 2.0",
    include_package_data=True,
    keywords="taipy-gui",
    name="taipy-gui",
    packages=find_packages(where=root_folder, include=["taipy", "taipy.gui", "taipy.gui.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
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
