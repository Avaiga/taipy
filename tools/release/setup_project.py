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
import platform
import re
import subprocess
import sys
from pathlib import Path

import toml  # type: ignore


def get_requirements(pkg: str, env: str = "dev") -> list:
    # get requirements from the different setups in tools/packages (removing taipy packages)
    reqs = set()
    pkg_name = pkg if pkg == "taipy" else f"taipy-{pkg}"
    root_folder = Path(__file__).parent
    package_path = os.path.join(root_folder.parent, "packages", pkg_name)
    requirements_file = os.path.join(package_path, "setup.requirements.txt")
    if os.path.exists(requirements_file):
        reqs.update(Path(requirements_file).read_text("UTF-8").splitlines())
    if env == "dev":
        return [r for r in reqs if r and not r.startswith("taipy")]
    return list(reqs)


def update_pyproject(version_path: str, pyproject_path: str, env: str = "dev"):
    with open(version_path) as version_file:
        version = json.load(version_file)
        version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
        if vext := version.get("ext"):
            version_string = f"{version_string}.{vext}"

    pyproject_data = toml.load(pyproject_path)
    pyproject_data["project"]["version"] = version_string
    pyproject_data["project"]["urls"]["Release notes"] = f"https://docs.taipy.io/en/release-{version_string}/relnotes/"
    pyproject_data["project"]["dependencies"] = get_requirements(get_pkg_name(pyproject_path), env)

    with open(pyproject_path, "w", encoding="utf-8") as pyproject_file:
        toml.dump(pyproject_data, pyproject_file)


def _build_webapp(webapp_path: str):
    already_exists = Path(webapp_path).exists()
    if not already_exists:
        os.system("cd ../../frontend/taipy-gui/dom && npm ci")
        os.system("cd ../../frontend/taipy-gui && npm ci && npm run build")


def get_pkg_name(path: str) -> str:
    # The regex pattern
    pattern = r"([^/\\]+)[/\\]pyproject\.toml$"

    # Search for the pattern
    match = re.search(pattern, os.path.abspath(path))
    if not match:
        raise ValueError(f"Could not find package name in path: {path}")
    return match.group(1)


if __name__ == "__main__":
    _pyproject_path = os.path.join(sys.argv[1], "pyproject.toml")
    try:
        env = sys.argv[2]
    except IndexError:
        env = "dev"

    pkg = get_pkg_name(_pyproject_path)
    if pkg == "taipy":
        _version_path = os.path.join(sys.argv[1], "taipy", "version.json")
        _webapp_path = os.path.join(sys.argv[1], "taipy", "gui", "webapp", "index.html")
    else:
        _version_path = os.path.join(sys.argv[1], "version.json")
        _webapp_path = os.path.join(sys.argv[1], "webapp", "index.html")

    update_pyproject(_version_path, _pyproject_path, env)

    if pkg == "gui":
        _build_webapp(_webapp_path)

    if pkg == "taipy":
        subprocess.run(
            ["python", "bundle_build.py"],
            cwd=os.path.join("tools", "frontend"),
            check=True,
            shell=platform.system() == "Windows",
        )
