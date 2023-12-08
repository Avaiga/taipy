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

"""The setup script."""


import json
import subprocess
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

root_folder = Path(__file__).parent

readme = Path(root_folder / "README.md").read_text("UTF-8")

with open(root_folder / "taipy" / "version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

requirements = [
    "backports.zoneinfo>=0.2.1,<0.3;python_version<'3.9'",
    "cookiecutter>=2.1.1,<2.2",
    "toml>=0.10,<0.11",
    "deepdiff>=6.2,<6.3",
    "pyarrow>=10.0.1,<11.0",
    "networkx>=2.6,<3.0",
    "openpyxl>=3.1.2,<3.2",
    "modin[dask]>=0.23.0,<1.0",
    "pymongo[srv]>=4.2.0,<5.0",
    "sqlalchemy>=2.0.16,<2.1",
    "flask>=3.0.0,<3.1",
    "flask-cors>=4.0.0,<5.0",
    "flask-socketio>=5.3.6,<6.0",
    "markdown>=3.4.4,<4.0",
    "pandas>=2.0.0,<3.0",
    "python-dotenv>=1.0.0,<1.1",
    "pytz>=2021.3,<2022.2",
    "tzlocal>=3.0,<5.0",
    "backports.zoneinfo>=0.2.1,<0.3;python_version<'3.9'",
    "gevent>=23.7.0,<24.0",
    "gevent-websocket>=0.10.1,<0.11",
    "kthread>=0.2.3,<0.3",
    "gitignore-parser>=0.1,<0.2",
    "simple-websocket>=0.10.1,<1.0",
    "twisted>=23.8.0,<24.0",
    "flask-restful>=0.3.9,<0.4",
    "passlib>=1.7.4,<1.8",
    "marshmallow>=3.20.1,<3.30",
    "apispec[yaml]>=6.3,<7.0",
    "apispec-webframeworks>=0.5.2,<0.6",
    "boto3>=1.29.1",
]


def get_requirements():
    # TODO get requirements from the different setups in tools/packages (removing taipy packages)
    return requirements


test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5.1,<6.0"],
    "image": [
        "python-magic>=0.4.24,<0.5;platform_system!='Windows'",
        "python-magic-bin>=0.4.14,<0.5;platform_system=='Windows'",
    ],
    "rdp": ["rdp>=0.8"],
    "arrow": ["pyarrow>=10.0.1,<11.0"],
    "mssql": ["pyodbc>=4"],
}


class NPMInstall(build_py):
    def run(self):
        subprocess.run(["python", "bundle_build.py"], cwd=root_folder / "tools" / "frontend", check=True, shell=True)
        build_py.run(self)


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
    ],
    description="A 360° open-source platform from Python pilots to production-ready web apps.",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "taipy = taipy._entrypoint:_entrypoint",
        ]
    },
    license="Apache License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="taipy",
    name="taipy",
    packages=find_packages(include=["taipy", "taipy.*"]),
    include_package_data=True,
    test_suite="tests",
    url="https://github.com/avaiga/taipy",
    version=version_string,
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
