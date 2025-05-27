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
# Returns the latest released versions for every Taipy package that is compatible with the target
# version (major and minor numbers match).
# The target package's version is set to the target version.
#
# Invoked from the workflow in publish.yml.
# --------------------------------------------------------------------------------------------------

import os
import sys

from common import PACKAGES


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <root_path> <version>")  # noqa: T201
    print("   Checks that all <package>-<version> archives exist in <root_path>.")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        raise ValueError("Missing arguments.")

    _path = sys.argv[1]
    _version = sys.argv[2]

    for package in [f"taipy-{_version}.tar.gz"] + [f"taipy-{p}-{_version}.tar.gz" for p in PACKAGES]:
        if not os.path.exists(os.path.join(_path, package)):
            print(f"Package {package} does not exist")  # noqa: T201
            sys.exit(1)
