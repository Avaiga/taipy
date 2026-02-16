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
# Deletes dev releases and tags for a specific version from a GitHub repository.
# --------------------------------------------------------------------------------------------------

import argparse

import requests
from common import Git, Version, fetch_github_releases


def main(arg_strings=None):
    parser = argparse.ArgumentParser(
        description="Deletes Taipy package dev releases and tags from GitHub.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "version",
        action="store",
        type=Version.check_argument,
        help="""The version (M.m.p) of the releases to be deleted.
The indicated version must not have extensions.""",
    )

    args = parser.parse_args(arg_strings)

    github_path = Git.get_github_path()
    all_releases = fetch_github_releases(github_path)
    found_dev_version_to_delete = False
    if all_releases:
        for package, releases in all_releases.items():
            for release in releases:
                release_version: Version = release["version"]
                release_id = release["id"]
                release_tag = release["tag"]
                if release_version.validate_extension() and args.version.match(release_version):
                    pkg = package.name
                    found_dev_version_to_delete = True

                    # Delete release
                    url = f"https://api.github.com/repos/{github_path}/releases/{release_id}"
                    response = requests.delete(url, headers={"Accept": "application/vnd.github+json"})
                    if response.status_code == 204:
                        print(f"✅ Successfully deleted '{pkg}-{release_version}'.")  # noqa: T201
                    else:
                        status = response.status_code
                        txt = response.text
                        print(f"❌ Failed to delete '{pkg}-{release_version}': {status} - {txt}")# noqa: T201

                    # Delete tag
                    url = f"https://api.github.com/repos/{github_path}/git/refs/tags/{release_tag}'"
                    response = requests.delete(url, headers={"Accept": "application/vnd.github+json"})
                    if response.status_code == 204:
                        print(f"✅ Successfully deleted tag {release_tag}.")  # noqa: T201
                    else:
                        status = response.status_code
                        txt = response.text
                        print(f"❌ Failed to delete tag {release_tag}: {status} - {txt}")  # noqa: T201

    if not found_dev_version_to_delete:
        print(f"No dev releases found for version {args.version}.")  # noqa: T201


if __name__ == "__main__":
    main()
