import os
import sys
from typing import Dict

BASE_PATH = "./tools/packages"


def __build_taipy_package_line(line: str, version: str) -> str:
    return f"{line.strip()} @ https://github.com/Avaiga/taipy/releases/download/{version}/{version}.tar.gz\n"


def update_setup_requirements(package: str, versions: Dict) -> None:
    _path = os.path.join(BASE_PATH, package, "setup.requirements.txt")
    lines = []
    with open(_path, mode="r") as req:
        for line in req:
            if v := versions.get(line.strip()):
                line = __build_taipy_package_line(line, v)
            lines.append(line)

    with open(_path, 'w') as file:
        file.writelines(lines)


if __name__ == "__main__":
    _package = sys.argv[1]
    _versions = {
        "taipy-config": sys.argv[2],
        "taipy-core": sys.argv[3],
        "taipy-gui": sys.argv[4],
        "taipy-rest": sys.argv[5],
        "taipy-templates": sys.argv[6],
    }

    update_setup_requirements(_package, _versions)
