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

import requests  # type: ignore


def fetch_latest_releases_from_github(dev=False, target_version="", target_package=""):
    releases = {}
    url = "https://api.github.com/repos/Avaiga/taipy/releases"
    response = requests.get(url)
    resp_json = response.json()

    for rel in resp_json:
        tag = rel["tag_name"]

        if not dev and ".dev" in tag:
            continue
        if "common" in tag:
            releases["common"] = releases.get("common") or tag.split("-")[0]
        elif "core" in tag:
            releases["core"] = releases.get("core") or tag.split("-")[0]
        elif "gui" in tag:
            releases["gui"] = releases.get("gui") or tag.split("-")[0]
        elif "rest" in tag:
            releases["rest"] = releases.get("rest") or tag.split("-")[0]
        elif "templates" in tag:
            releases["templates"] = releases.get("templates") or tag.split("-")[0]
        elif "-" not in tag:
            releases["taipy"] = releases.get("taipy") or tag
    releases[target_package] = target_version
    return releases


def fetch_latest_releases_from_pypi(dev=False, target_version="", target_package=""):
    releases = {}

    for pkg in ["common", "core", "gui", "rest", "templates"]:
        url = f"https://pypi.org/pypi/taipy-{pkg}/json"
        response = requests.get(url)
        resp_json = response.json()
        versions = list(resp_json["releases"].keys())
        versions.reverse()

        for ver in versions:
            if not dev and ".dev" in ver:
                continue
            releases[pkg] = ver
            break
    releases[target_package] = target_version
    return releases


if __name__ == "__main__":
    is_dev_version = sys.argv[1] == "dev"
    is_pypi = sys.argv[2] == "true"
    target_version = sys.argv[3]
    target_package = sys.argv[4]

    if is_dev_version and ".dev" not in target_version:
        raise Exception("Version does not contain suffix .dev")

    versions = {}

    if not is_pypi:
        versions = fetch_latest_releases_from_github(is_dev_version, target_version, target_package)
    else:
        versions = fetch_latest_releases_from_pypi(is_dev_version, target_version, target_package)

    for name, version in versions.items():
        print(f"{name}_VERSION={version}")  # noqa: T201
