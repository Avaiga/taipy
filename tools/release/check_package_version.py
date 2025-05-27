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
# Checks that the version declared in <package_dir>/version.json matches a given version.
# --------------------------------------------------------------------------------------------------

import json
import os
import sys

from common import Package, Version


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <package> <version>")  # noqa: T201
    print("   Checks that the version defined in the <package>'s version.json file is <version>.")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        raise ValueError("Missing arguments.")
    package = Package(sys.argv[1])
    version = Version.from_string(sys.argv[2])

    # Check that build version matches package's version.json
    with open(os.path.join(package.package_dir, "version.json")) as version_file:
        package_version = Version(**json.load(version_file))
        if version != package_version:
            raise ValueError(
                f"Version mismatch for package {package}: "
                + f"building '{version}' but '{package_version}' is defined in 'version.json'."
            )
    # Check Taipy GUI and Taipy packages bundle versions
    package_json_path = None
    if package.name == "taipy":
        package_json_path = "frontend/taipy/package.json"
    elif package.short_name == "gui":
        package_json_path = "frontend/taipy-gui/package.json"
    if package_json_path:
        with open(package_json_path) as package_file:
            package_config = json.load(package_file)
            package_version = Version.from_string(package_config["version"])
            if version != package_version:
                raise ValueError(
                    f"Version mismatch for frontend of package {package}: "
                    + f"building '{version}' but '{package_version}' is defined in '{package_json_path}'."
                )
