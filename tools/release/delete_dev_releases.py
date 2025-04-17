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

    def _check_repository_path(value: str):
        if len(value.split("/")) != 2:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid '<owner>/<repo>' path.")
        return value

    parser.add_argument(
        "-r",
        "--repository_path",
        type=_check_repository_path,
        help="""The '<owner>/<repo>' string that identifies the repository where releases are fetched.
The default is the current repository.""",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="""Do not ask for confirmation of the deletion of the releases and tags.""",
    )
    args = parser.parse_args(arg_strings)

    headers = {"Accept": "application/vnd.github+json"}
    repository_path = args.repository_path if args.repository_path else Git.get_github_path()
    all_releases = fetch_github_releases(repository_path)
    found = False
    if all_releases:
        for package, releases in all_releases.items():
            for release in releases:
                release_version = release["version"]
                release_id = release["id"]
                release_tag = release["tag"]
                if release_version.validate_extension() and args.version.match(release_version):
                    found = True
                    confirm = True if args.yes else False
                    if not args.yes:
                        print(f"\n➡️ Release: package: {package.name}, version: {release_version}")  # noqa: T201
                        confirm = (
                            input("❓ Do you want to delete this release and its tag? (y/N): ").strip().lower() != "y"
                        )
                    if confirm:
                        # Delete release
                        url = f"https://api.github.com/repos/{repository_path}/releases/{release_id}"
                        response = requests.delete(url, headers=headers)
                        if response.status_code == 204:
                            print(f"✅ Successfully deleted release {release_version} for package '{package.name}'.")  # noqa: T201
                        else:
                            print(  # noqa: T201
                                f"❌ Failed to delete release {release_version} for package '{package.name}':"
                                + f" {response.status_code} - {response.text}"
                            )
                        # Delete tag
                        url = f"https://api.github.com/repos/{repository_path}/git/refs/tags/{release_tag}'"
                        response = requests.delete(url, headers=headers)
                        if response.status_code == 204:
                            print(f"✅ Successfully deleted tag {release_tag}.")  # noqa: T201
                        else:
                            print(f"❌ Failed to delete tag {release_tag}: {response.status_code} - {response.text}")  # noqa: T201
                    else:
                        print("ℹ️ Skipped.")  # noqa: T201

    if not found:
        print(f"No dev releases found for version {args.version}.")  # noqa: T201


if __name__ == "__main__":
    main()
