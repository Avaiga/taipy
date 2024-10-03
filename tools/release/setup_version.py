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
import re
import sys
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Version:
    major: str
    minor: str
    patch: str
    ext: Optional[str] = None

    def bump_ext_version(self) -> None:
        if not self.ext:
            return
        reg = re.compile(r"[0-9]+$")
        num = reg.findall(self.ext)[0]

        self.ext = self.ext.replace(num, str(int(num) + 1))

    def validate_suffix(self, suffix="dev"):
        if suffix not in self.ext:
            raise Exception(f"Version does not contain suffix {suffix}")

    @property
    def name(self) -> str:
        """returns a string representation of a version"""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def dev_name(self) -> str:
        """returns a string representation of a version"""
        return f"{self.name}.{self.ext}"

    def __str__(self) -> str:
        """returns a string representation of a version"""
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.ext:
            version_str = f"{version_str}.{self.ext}"
        return version_str


def __load_version_from_path(base_path: str) -> Version:
    """Load version.json file from base path."""
    with open(os.path.join(base_path, "version.json")) as version_file:
        data = json.load(version_file)
        return Version(**data)


def __write_version_to_path(base_path: str, version: Version) -> None:
    with open(os.path.join(base_path, "version.json"), "w") as version_file:
        json.dump(asdict(version), version_file)


def extract_version(base_path: str) -> Version:
    """
    Load version.json file from base path and return the version string.
    """
    return __load_version_from_path(base_path)


def __setup_dev_version(version: Version, _base_path: str, name: Optional[str] = None) -> None:
    version.validate_suffix()

    name = f"{name}_VERSION" if name else "VERSION"
    print(f"{name}={version.dev_name}")  # noqa: T201

    version.bump_ext_version()

    __write_version_to_path(_base_path, version)
    print(f"NEW_{name}={version.dev_name}")  # noqa: T201


def __setup_prod_version(version: Version, target_version: str, branch_name: str, name: str = None) -> None:
    if str(version) != target_version:
        raise ValueError(f"Current version={version} does not match target version={target_version}")

    if target_branch_name := f"release/{version.major}.{version.minor}" != branch_name:
        raise ValueError(
            f"Branch name mismatch branch={branch_name} does not match target branch name={target_branch_name}"
        )

    name = f"{name}_VERSION" if name else "VERSION"
    print(f"{name}={version.name}")  # noqa: T201


if __name__ == "__main__":
    paths = (
        [sys.argv[1]]
        if sys.argv[1] != "ALL"
        else [
            f"taipy{os.sep}common",
            f"taipy{os.sep}core",
            f"taipy{os.sep}rest",
            f"taipy{os.sep}gui",
            f"taipy{os.sep}templates",
            "taipy",
        ]
    )
    _environment = sys.argv[2]

    for _path in paths:
        _version = extract_version(_path)
        _name = None if _path == "taipy" else _path.split(os.sep)[-1]

        if _environment == "dev":
            __setup_dev_version(_version, _path, _name)

        if _environment == "production":
            __setup_prod_version(_version, sys.argv[3], sys.argv[4], _name)
