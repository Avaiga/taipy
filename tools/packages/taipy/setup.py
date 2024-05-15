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

"""The setup script for taipy package"""

import json
import platform
from pathlib import Path
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

package_desc = (root_folder / "package_desc.md").read_text("UTF-8")

with open(root_folder / "taipy" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [r for r in (root_folder / "setup.requirements.txt").read_text("UTF-8").splitlines() if r]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "rdp": ["rdp>=0.8"],
    "arrow": ["pyarrow>=14.0.2,<15.0"],
    "mssql": ["pyodbc>=4"],
}


class NPMInstall(build_py):
    def run(self):
        subprocess.run(
            ["python", "bundle_build.py"],
            cwd=root_folder / "tools" / "frontend",
            check=True,
            shell=platform.system() == "Windows",
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
    description="A 360° open-source platform from Python pilots to production-ready web apps.",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "taipy = taipy._entrypoint:_entrypoint",
        ]
    },
    license="Apache License 2.0",
    long_description=package_desc,
    long_description_content_type="text/markdown",
    keywords="taipy",
    name="taipy",
    packages=find_packages(include=["taipy", "taipy._cli", "taipy._cli.*", "taipy.gui_core"]),
    include_package_data=True,
    test_suite="tests",
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
