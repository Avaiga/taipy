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

import os
import sys

if __name__ == "__main__":
    _path = sys.argv[1]
    _version = sys.argv[2]

    packages = [
        f"taipy-{_version}.tar.gz",
        f"taipy-common-{_version}.tar.gz",
        f"taipy-core-{_version}.tar.gz",
        f"taipy-rest-{_version}.tar.gz",
        f"taipy-gui-{_version}.tar.gz",
        f"taipy-templates-{_version}.tar.gz",
    ]

    for package in packages:
        if not os.path.exists(os.path.join(_path, package)):
            print(f"Package {package} does not exist")  # noqa: T201
            sys.exit(1)
