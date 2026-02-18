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
# Checks that build version matches package(s) version.
#
# Invoked from the workflow in build-and-release.yml.
#
# Outputs a line for each package (all packages if 'all'):
#   <package_short_name>_VERSION=<release_version>
#      the release version of the package that gets built.
#      - if 'dev' release mode, that would be M.m.p.dev<x>
#        where dev<x> is the first available available release version number that has no release yet.
#      - if 'production' release mode, that would be M.m.p, as read in the packages's version.json
#        file.
# If a 'production' release mode is requested, a similar line is issued indicating the next patch
# version number:
#   NEXT_<package_short_name>_VERSION=<next_release_version>
# --------------------------------------------------------------------------------------------------

import argparse
import os

from common import Git, Package, Version, fetch_github_releases, fetch_latest_github_taipy_releases


def __setup_dev_version(
    package: Package, version: Version, released_versions: list[Version], target_version: dict[str, Version]
) -> None:
    # Find latest dev release for that version
    ext_index = 0
    matching_versions = [v for v in released_versions if v.matches(version) and v.validate_extension()]
    latest_version = (max(matching_versions) if matching_versions else None)
    ext, ext_index = ("dev", 0)
    if latest_version:
        ext, ext_index = latest_version.split_ext()
        ext_index += 1
    target_version[package.short_name] = Version(version.major, version.minor, version.patch, f"{ext}{ext_index}")


def __setup_prod_version(
    package: Package,
    version: Version,
    branch_name: str,
    target_versions: dict[str, Version],
    next_versions: dict[str, Version],
) -> None:
    # Production releases can only be performed from a release branch
    if (os.environ.get("GITHUB_ACTIONS") == "true") and (
        target_branch_name := f"release/{version.major}.{version.minor}"
    ) != branch_name:
        raise ValueError(f"Current branch '{branch_name}' does not match expected '{target_branch_name}'")
    target_versions[package.short_name] = version
    # Compute next patch version
    next_versions[package.short_name] = Version(version.major, version.minor, version.patch + 1)


def main():
    parser = argparse.ArgumentParser(
        description="Computes the Taipy package versions to be build.", formatter_class=argparse.RawTextHelpFormatter
    )

    # <package> argument
    def _check_package(value: str) -> str:
        n_value = value.lower()
        if n_value in Package.names(True) or value == "all":
            return n_value
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid Taipy package name.")

    parser.add_argument(
        "package",
        type=_check_package,
        action="store",
        help="""The name of the package to setup the build version for.
This should be the short name of a Taipy package (common, core...) or 'taipy'.
If can also be set to 'ALL' then all versions for all packages are computed.
""",
    )

    # <version> argument
    parser.add_argument(
        "-v",
        "--version",
        type=Version.check_argument,
        required=True,
        help="""Full name of the target version (M.m.p).
This version must match the one in the package's 'version.json' file.
""",
    )
    # <release_type> argument
    parser.add_argument(
        "-t",
        "--release_type",
        choices=["dev", "production"],
        default="dev",
        type=str.lower,
        help="""Type of release to build (default: dev).

If 'dev', the release version is computed from the existing released packages versions
in the repository:
- If there is no release with version <version>, the release will have the version set
  to <version>.dev0.
- If there is a <version>.dev<n> release, the release will have the version <version>.dev<n+1>.
- If there is a <version> release (with no 'dev' part), the script fails.

If 'production', the package version is computed from for existing released packages versions
""",
    )

    # <repository_name> argument
    def _check_repository_name(value: str) -> str:
        if len(value.split("/")) != 2:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid '<owner>/<repo>' pair.")
        return value

    parser.add_argument(
        "-r",
        "--repository_name",
        type=_check_repository_name,
        help="""The '<owner>/<repo>' string that identifies the repository where releases are fetched.
The default is the current repository.""",
    )
    # <branch_name> argument
    parser.add_argument(
        "-b",
        "--branch_name",
        help="""The name of the branch to check package versions from."
If <release_type> is 'production', this branch has to be a release branch ('release/*').
This value is extracted from the current branch by default.
        """,
    )
    args = parser.parse_args()

    all_releases = fetch_github_releases(args.repository_name)
    target_versions = {}
    next_versions = {}
    for package_name in Package.names(True):
        package_releases = all_releases.get(Package(package_name))
        released_versions = [release["version"] for release in package_releases] if package_releases else []
        if args.release_type == "production":
            released_versions = list(filter(lambda v: v.ext is None, released_versions))
        else:
            released_versions = list(filter(lambda v: v.ext is not None, released_versions))
        # Matching versions
        released_versions = [v for v in released_versions if v.matches(args.version, Version.MINOR)]
        target_version = max(released_versions) if released_versions else None
        target_versions[package_name] = target_version if target_version else Version.UNKNOWN

    packages: list[str] = [args.package] if args.package != "all" else Package.names(True)
    branch_name = args.branch_name if args.branch_name else Git.get_current_branch()

    for package_name in packages:
        package = Package(package_name)
        version = package.load_version()
        if version.ext:
            raise ValueError(f"Package version for '{package.name}' has an extension ({version.full_name}).")
        if version != args.version:
            raise ValueError(
                f"Target version ({args.version.full_name}) does not match version"
                + f" {version.full_name} in package {package.name}."
            )
        package_releases = all_releases.get(package)
        released_versions = [release["version"] for release in package_releases] if package_releases else []
        if version in released_versions:
            raise ValueError(f"{version} is already released for package {package.name}.")

        if args.release_type == "dev":
            __setup_dev_version(package, version, released_versions, target_versions)
        else:
            __setup_prod_version(package, version, branch_name, target_versions, next_versions)

    for p, v in target_versions.items():
        print(f"{p}_VERSION={v}")  # noqa: T201
    if next_versions:
        for p, v in next_versions.items():
            print(f"NEXT_{p}_VERSION={v}")  # noqa: T201

    # Print out the 'taipy' version that should be tagged latest at the end of the workflow
    latest_release = fetch_latest_github_taipy_releases(all_releases)
    if args.release_type == "production":
        if not target_versions.get("taipy", Version.UNKNOWN) < latest_release:
            latest_release = target_versions["taipy"]
    print(f"LATEST_TAIPY_VERSION={latest_release}")  # noqa: T201


if __name__ == "__main__":
    main()
