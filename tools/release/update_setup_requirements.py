# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# --------------------------------------------------------------------------------------------------
# Updates the setup.requirements.txt files for a given package.
#
# Invoked by workflows/build-and-release-single-package.yml and workflows/build-and-release.yml.
# Working directory must be [root_dir].
# --------------------------------------------------------------------------------------------------

import argparse
import os
import re
import typing as t

from common import Git, Package, Version

BASE_PATH = "./tools/packages"


def __build_taipy_package_line(line: str, version: Version, use_pypi: bool, gh_path: t.Optional[str]) -> str:
    line = line.strip()
    if use_pypi:
        # Target dependency version should the latest compatible with 'version'
        return f"{line} >={version.major}.{version.minor},<{version.major}.{version.minor + 1}\n"
    tag = f"{version}-{line.split('-')[1]}"
    tar_name = f"{line}-{version}"
    return f"{line} @ https://github.com/{gh_path}/releases/download/{tag}/{tar_name}.tar.gz\n"


def update_setup_requirements(
    package: Package, versions: dict[str, Version], publish_on_py_pi: bool, gh_path: t.Optional[str]
) -> None:
    path = os.path.join(BASE_PATH, package.name, "setup.requirements.txt")
    lines = []
    with open(path, mode="r") as req:
        for line in req:
            if match := re.match(r"^taipy(:?\-\w+)?\s*", line, re.MULTILINE):
                # Add subpackage version if not forced
                if not line[match.end() :] and (v := versions.get(line.strip())):
                    if v == Version.UNKNOWN:
                        raise ValueError(f"Missing version for dependency '{line.strip()}'.")
                    line = __build_taipy_package_line(line, v, publish_on_py_pi, gh_path)
            lines.append(line)

    with open(path, "w") as file:
        file.writelines(lines)
    # Issue the generated files for logging information
    print(f"Generated setup.requirements.txt for package '{package}'")  # noqa: T201
    for line in lines:
        print(line.strip())  # noqa: T201
    print("-" * 32)  # noqa: T201


def main():
    parser = argparse.ArgumentParser(
        description="Computes the Taipy package versions to be build.", formatter_class=argparse.RawTextHelpFormatter
    )

    # <package> argument
    parser.add_argument(
        "package",
        type=Package,
        action="store",
        help="""The name of the package to setup the build version for.
This must be the short name of a Taipy package (common, core...) or 'taipy'.
""",
    )

    # <common-version> argument
    parser.add_argument(
        "common_version",
        type=Version.check_argument,
        action="store",
        help="Full name of the target version (M.m.p) for the taipy-common package.",
    )
    # <core-version> argument
    parser.add_argument(
        "core_version",
        type=Version.check_argument,
        action="store",
        help="Full name of the target version (M.m.p) for the taipy-core package.",
    )
    # <gui-version> argument
    parser.add_argument(
        "gui_version",
        type=Version.check_argument,
        action="store",
        help="Full name of the target version (M.m.p) for the taipy-gui package.",
    )
    # <rest-version> argument
    parser.add_argument(
        "rest_version",
        type=Version.check_argument,
        action="store",
        help="Full name of the target version (M.m.p) for the taipy-rest package.",
    )
    # <rest-version> argument
    parser.add_argument(
        "templates_version",
        type=Version.check_argument,
        action="store",
        help="Full name of the target version (M.m.p) for the taipy-templates package.",
    )
    # <dependencies-location> argument
    parser.add_argument(
        "-deps",
        "-dl",
        "--dependencies-location",
        type=str.lower,
        choices=["github", "pypi"],
        required=True,
        help="Where to point dependencies to.",
    )

    # <repository_name> argument
    def _check_repository_name(value: str) -> str:
        if len(value.split("/")) != 2:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid '<owner>/<repo>' pair.")
        return value

    parser.add_argument(
        "-r",
        "--repository_name",
        type=_check_repository_name,
        help="""The '<owner>/<repo>' string that identifies the repository where releases are fetched.
The default is the current repository.""",
    )

    args = parser.parse_args()
    versions = {
        "taipy-common": args.common_version,
        "taipy-core": args.core_version,
        "taipy-gui": args.gui_version,
        "taipy-rest": args.rest_version,
        "taipy-templates": args.templates_version,
    }
    publish_on_py_pi = args.dependencies_location == "pypi"
    repository_name = args.repository_name if args.repository_name else Git.get_github_path()
    update_setup_requirements(args.package, versions, publish_on_py_pi, repository_name)


if __name__ == "__main__":
    main()
