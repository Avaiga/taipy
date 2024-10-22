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
from typing import Dict

BASE_PATH = "./tools/packages"


def __build_taipy_package_line(line: str, version: str, publish_on_py_pi: bool) -> str:
    _line = line.strip()
    if publish_on_py_pi:
        return f"{_line}=={version}\n"
    tag = f"{version}-{_line.split('-')[1]}"
    tar_name = f"{_line}-{version}"
    return f"{_line} @ https://github.com/Avaiga/taipy/releases/download/{tag}/{tar_name}.tar.gz\n"


def update_setup_requirements(package: str, versions: Dict, publish_on_py_pi: bool) -> None:
    _path = os.path.join(BASE_PATH, package, "setup.requirements.txt")
    lines = []
    with open(_path, mode="r") as req:
        for line in req:
            if v := versions.get(line.strip()):
                line = __build_taipy_package_line(line, v, publish_on_py_pi)
            lines.append(line)

    with open(_path, "w") as file:
        file.writelines(lines)


if __name__ == "__main__":
    _package = sys.argv[1]
    _versions = {
        "taipy-common": sys.argv[2],
        "taipy-core": sys.argv[3],
        "taipy-gui": sys.argv[4],
        "taipy-rest": sys.argv[5],
        "taipy-templates": sys.argv[6],
    }
    _publish_on_py_pi = True if sys.argv[7] == "true" else False

    update_setup_requirements(_package, _versions, _publish_on_py_pi)
