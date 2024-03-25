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

import sys


def update_setup() -> None:
    with open("setup.taipy.py", mode="r") as setup_r, open("setup.py", mode="w") as setup_w:
        in_requirements = False
        looking = True
        for line in setup_r:
            if looking:
                if line.lstrip().startswith("requirements") and line.rstrip().endswith("["):
                    in_requirements = True
                elif in_requirements:
                    if line.strip() == "]":
                        looking = False
                    else:
                        if line.lstrip().startswith('"taipy-gui@git+https'):
                            start = line.find('"taipy-gui')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-gui=={sys.argv[1]}"{line[end:]}'
                        elif line.lstrip().startswith('"taipy-rest@git+https'):
                            start = line.find('"taipy-rest')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-rest=={sys.argv[2]}"{line[end:]}'
                        elif line.lstrip().startswith('"taipy-templates@git+https'):
                            start = line.find('"taipy-templates')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-templates=={sys.argv[3]}"{line[end:]}'
            setup_w.write(line)


if __name__ == "__main__":
    update_setup()
