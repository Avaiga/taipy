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
import os

import requests
from common import Git, Version, fetch_github_releases


def main(arg_strings=None):
    parser = argparse.ArgumentParser(
        description="Deletes Taipy package dev releases and tags from GitHub.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="store",
        type=Version.check_argument,
        help="""The version (M.m.p) of the releases to be deleted.
The indicated version must not have extensions.""",
    )

    parser.add_argument(
        "--dry_run",
        type=str.lower,
        default="True",
        help="A boolean flag indicating whether to perform a dry run (default: True). " +
             "If set to True, the script will only print the releases and tags that would " +
             "be deleted without actually deleting them. This can be useful for verifying " +
             " which releases and tags would be affected before performing the actual deletion.")

    parser.add_argument(
        "--extension",
        type=str,
        default="dev",
        help="The extension to look for in the releases to be deleted (default: 'dev'). ")

    args = parser.parse_args(arg_strings)
    version = args.version
    extension = args.extension
    token = os.environ.get("GITHUB_TOKEN")
    dry_run = args.dry_run.strip().lower() in ("true", "1", "yes")
    if dry_run:
        print("⚠️  DRY RUN MODE ENABLED ⚠️")  # noqa: T201

    github_path = Git.get_github_path()
    all_releases = fetch_github_releases(github_path)
    del_releases = []
    del_tags = []
    found_wrong_version = []
    found_wrong_extension = []
    errors = []
    if all_releases:
        for package, releases in all_releases.items():
            for release in releases:
                release_version: Version = release["version"]
                if release_version.has_extension():
                    release_id = release["id"]
                    release_tag = release["tag"]
                    if version.matches(release_version) and release_version.validate_extension(ext=extension):

                        if not __delete_release(dry_run, github_path, token, package.name, release_id, release_version):
                            errors.append(f"Release {release_version}-{package.name} (id: {release_id})")
                        else:
                            del_releases.append(release_id)
                        if not __delete_tag(dry_run, github_path, token, release_tag):
                            errors.append(f"Tag {release_tag}")
                        else:
                            del_tags.append(release_tag)
                    elif not version.matches(release_version) and release_version.validate_extension(ext=extension):
                        found_wrong_version.append(release_tag)
                    elif version.matches(release_version):
                        found_wrong_extension.append(release_tag)

    beautiful_traces(version, extension, del_releases, del_tags, errors, found_wrong_extension, found_wrong_version)


def beautiful_traces(version, extension, del_releases, del_tags, errors, found_wrong_extension, found_wrong_version):
    print(" ")  # noqa: T201
    if len(del_releases) == 0:
        print(f"No dev releases deleted for version {version}.")  # noqa: T201
    else:
        print(  # noqa: T201
            f"✅ Successfully deleted {len(del_releases)} releases {version} " +  # noqa: T201
            f"with extension '{extension}'")  # noqa: T201
    if len(del_tags) == 0:
        print(f"No tags deleted for version {version} with extension '{extension}'.")  # noqa: T201
    else:
        print(  # noqa: T201
            f"✅ Successfully deleted {len(del_tags)} tags for version " +  # noqa: T201
            f"{version} with extension '{extension}'")  # noqa: T201
    if len(errors) > 0:
        print(f"❌ Failed to delete {len(errors)} items.")  # noqa: T201
    print(" ") # noqa: T201
    if len(found_wrong_extension) > 0:
        print(  # noqa: T201
            f"Found {len(found_wrong_extension)} releases matching version " +  # noqa: T201
            f"{version} but with another extension:")  # noqa: T201
        print(sorted(found_wrong_extension))  # noqa: T201
    if len(found_wrong_version) > 0:
        print(  # noqa: T201
            f"Found {len(found_wrong_version)} releases matching extension " +  # noqa: T201
            f"'{extension}' but with another version:")  # noqa: T201
        print(sorted(found_wrong_version))  # noqa: T201


def __delete_release(dry_run, github_path: str, token: str, pkg: str, release_id: str, rel_version: Version) -> bool:
    url = f"https://api.github.com/repos/{github_path}/releases/{release_id}"
    if dry_run:
        print(f'requests.delete("{url}", ' +  # noqa: T201
              'headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer ' + "<token>" +  # noqa: T201
              '", "X-GitHub-Api-Version": "2022-11-28"})')  # noqa: T201
        return True
    else:
        resp = requests.delete(url, headers={"Accept": "application/vnd.github+json",
                                             "Authorization": f"Bearer {token}",
                                             "X-GitHub-Api-Version": "2022-11-28"})
        if resp.status_code == 204:
            print(f"Successfully deleted '{pkg}-{rel_version}'.")  # noqa: T201
            return True
        else:
            print(f"❌ Failed deleting '{pkg}-{rel_version}': {resp.status_code} - {resp.text}")  # noqa: T201
            return False


def __delete_tag(dry_run, github_path: str, token: str, release_tag: str) -> bool:
    url = f"https://api.github.com/repos/{github_path}/git/refs/tags/{release_tag}"
    if dry_run:
        print(f'requests.delete("{url}", ' +  # noqa: T201
              'headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer ' + "<token>" +  # noqa: T201
              '", "X-GitHub-Api-Version": "2022-11-28"})')  # noqa: T201
        return True
    else:
        resp = requests.delete(url, headers={"Accept": "application/vnd.github+json",
                                             "Authorization": f"Bearer {token}",
                                             "X-GitHub-Api-Version": "2022-11-28"})
        if resp.status_code == 204:
            print(f"Successfully deleted tag {release_tag}.")  # noqa: T201
            return True
        else:
            print(f"❌ Failed to delete tag {release_tag}: {resp.status_code} - {resp.text}")  # noqa: T201
            return False


if __name__ == "__main__":
    main()
