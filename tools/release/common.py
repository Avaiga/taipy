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
# Common artifacts used by the other scripts located in this directory.
# --------------------------------------------------------------------------------------------------
import argparse
import json
import os
import re
import subprocess
import typing as t
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import requests


# --------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Version:
    """Helps manipulate version numbers."""

    major: int
    minor: int
    patch: int = 0
    ext: t.Optional[str] = None

    # Matching level
    MAJOR: t.ClassVar[int] = 1
    MINOR: t.ClassVar[int] = 2
    PATCH: t.ClassVar[int] = 3

    # Unknown version constant
    UNKNOWN: t.ClassVar["Version"]

    @property
    def name(self) -> str:
        """Returns a string representation of this Version without the extension part."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def full_name(self) -> str:
        """Returns a full string representation of this Version."""
        return f"{self.name}.{self.ext}" if self.ext else self.name

    def __str__(self) -> str:
        """Returns a string representation of this version."""
        return self.full_name

    def __repr__(self) -> str:
        """Returns a full string representation of this version."""
        ext = f".{self.ext}" if self.ext else ""
        return f"Version({self.major}.{self.minor}.{self.patch}{ext})"

    @classmethod
    def from_string(cls, version: str):
        """Creates a Version from a string.

        Arguments:
            version: a version name as a string.<br/>
              The format should be "<major>.<minor>[.<patch>[.<extension>]] where

              - <major> must be a number, indicating the major number of the version
              - <minor> must be a number, indicating the minor number of the version
              - <patch> must be a number, indicating the patch level of the version. Optional.
              - <extension> must be a string. It is common practice that <extension> ends with a
                number, but it is not required. Optional.
        Returns:
            A new Version object with the appropriate values that were parsed.
        """
        match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\.([^\s]+))?", version)
        if match:
            major = int(match[1])
            minor = int(match[2])
            patch = int(match[3]) if match[3] else 0
            ext = match[4]
            return cls(major=major, minor=minor, patch=patch, ext=ext)
        else:
            raise ValueError(f"String not in expected format: {version}")

    def to_dict(self) -> dict[str, str]:
        """Returns this Version as a dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @staticmethod
    def check_argument(value: str) -> "Version":
        """Checks version parameter in an argparse context."""
        try:
            version = Version.from_string(value)
        except Exception as e:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid version number.") from e
        return version

    def has_extension(self) -> bool:
        """Returns True if this Version has an extension part."""
        return self.ext is not None

    def validate_extension(self, ext="dev"):
        """Returns True if the extension part of this Version is the one queried."""
        return self.split_ext()[0] == ext

    def split_ext(self) -> t.Tuple[str, int]:
        """Splits extension into the (identifier, index) tuple

        Returns:
            ("", -1) if there is no extension.
            (extension, -1) if there is no extension index.
            (extension, index) if there is an extension index (e.g. "dev3").
        """
        if not self.ext or (match := re.fullmatch(r"(.*?)(\d+)?", self.ext)) is None:
            return ("", -1)  # No extension
        # Potentially no index
        return (match[1], int(match[2]) if match[2] else -1)

    def is_compatible(self, version: "Version") -> bool:
        """Checks if this version is compatible with another.

        Version v1 is defined as being compatible with version v2 if a package built with version v1
        can safely depend on another package built with version v2.<br/>
        Here are the conditions set when checking whether v1 is compatible with v2:

        - If v1 and v2 have different major or minor numbers, they are not compatible.
        - If v1 has no extension, it is compatible only with v2 that have no extension.
        - If v1 has an extension, it is compatible with any v2 that has the same extension, no
          matter the extension index.

        I.e.:
            package-1.[m].[t] is NOT compatible with any sub-package-[M].* where M != 1
            package-1.2.[t] is NOT compatible with any sub-package-1.[m].* where m != 2
            package-1.2.[t] is compatible with all sub-package-1.2.*
            package-1.2.[t].ext[X] is compatible with all sub-package-1.2.*.ext*
            package-1.2.3 is NOT compatible with any sub-package-1.2.*.*
            package-1.2.3.extA is NOT compatible with any sub-package-1.2.*.extB if extA != extB,
               independently of a potential extension index.

        Arguments:
            version: the version to check compatibility against.

        Returns:
            True is this Version is compatible with *version* and False if it is not.
        """
        if self.major != version.major or self.minor != version.minor:
            return False
        if self.patch > version.patch:
            return True

        # No extensions on either → Compatible
        if not self.ext and not version.ext:
            return True

        # self has extension, version doesn't → Compatible
        if self.ext and not version.ext:
            return True

        # Version has extension, self doesn't → Not compatible
        if not self.ext and version.ext:
            return False

        # Both have extensions → check identifiers. Dissimilar identifiers → Not compatible
        self_prefix, _ = self.split_ext()
        other_prefix, _ = version.split_ext()
        if self_prefix != other_prefix:
            return False

        # Same identifiers → Compatible
        return True

    def matches(self, version: "Version", level: int = PATCH) -> bool:
        """Checks whether this version matches another, up to some level.

        Arguments:
            version: The version to check against.
            level: The level of precision for the match:
            - Version.MAJOR: compare only the major version;
            - Version.MINOR: compare major and minor versions;
            - Version.PATCH: compare major, minor, and patch versions.

        Returns:
            True if the versions match up to the given level, False otherwise.
        """
        if self.major != version.major:
            return False
        if level >= self.MINOR and self.minor != version.minor:
            return False
        if level >= self.PATCH and self.patch != version.patch:
            return False
        return True

    def __lt__(self, other: "Version") -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major, minor, patch
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)
        if self_tuple != other_tuple:
            return self_tuple < other_tuple

        # Same version number, now compare extensions
        return self._ext_sort_key() < other._ext_sort_key()

    def _ext_sort_key(self) -> t.Tuple[int, str, int]:
        """
        Defines ordering for extensions.
        Final versions (None) are considered greater than prereleases.

        Example sort order:
        1.0.0.dev1 < 1.0.0.rc1 < 1.0.0 < 1.0.1
        """
        if self.ext is None:
            return (2, "", 0)  # Final release — highest priority

        # Parse extension like "dev1" into prefix + number
        match = re.match(r"([a-zA-Z]+)(\d*)", self.ext)
        if match:
            label, num = match.groups()
            num_val = int(num) if num else 0
            return (1, label, num_val)  # Pre-release
        else:
            return (0, self.ext, 0)  # Unknown extension format — lowest priority


Version.UNKNOWN = Version(0, 0)


# --------------------------------------------------------------------------------------------------
class Package:
    """Information on any Taipy package and sub-package."""

    # Base names of the sub packages taipy-*
    # They also are the names of the directory where their code belongs, under the 'taipy' directory,
    # in the root of the Taipy repository.
    # Order is important: package that are dependent of others must appear first.
    NAMES = ["common", "core", "gui", "rest", "templates"]

    _packages = {}

    def __new__(cls, name: str) -> "Package":
        if name.startswith("taipy-"):
            name = name[6:]
        if name in cls._packages:
            return cls._packages[name]
        package = super().__new__(cls)
        cls._packages[name] = package
        return package

    def __init__(self, package: str) -> None:
        self._name = package
        if package == "taipy":
            self._short = package
        else:
            if package.startswith("taipy-"):
                self._short = package[6:]
            else:
                self._name = f"taipy-{package}"
                self._short = package
            if self._short not in Package.NAMES:
                raise ValueError(f"Invalid package name '{package}'.")

    @classmethod
    def names(cls, add_taipy=False) -> list[str]:
        return cls.NAMES + (["taipy"] if add_taipy else [])

    @staticmethod
    def check_argument(value: str) -> str:
        """Checks package parameter in an argparse context."""
        n_value = value.lower()
        if n_value in Package.names(True) or value == "all":
            return n_value
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid Taipy package name.")

    @property
    def name(self) -> str:
        """The full package name."""
        return self._name

    @property
    def short_name(self) -> str:
        """The short package name."""
        return self._short

    @property
    def package_dir(self) -> str:
        return "taipy" if self._name == "taipy" else os.path.join("taipy", self._short)

    def load_version(self) -> Version:
        """
        Returns the Version defined in this package's version.json content.
        """
        with open(Path(self.package_dir) / "version.json") as version_file:
            data = json.load(version_file)
            return Version(**data)

    def save_version(self, version: Version) -> None:
        """
        Saves the Version to this package's version.json file.
        """
        with open(os.path.join(Path(self.package_dir), "version.json"), "w") as version_file:
            json.dump(version.to_dict(), version_file)

    def __str__(self) -> str:
        """Returns a string representation of this package."""
        return self.name

    def __repr__(self) -> str:
        """Returns a full string representation of this package."""
        return f"Package({self.name})"

    def __eq__(self, other):
        return isinstance(other, Package) and (self._short, self._short) == (other._short, other._short)

    def __hash__(self):
        return hash(self._short)


# --------------------------------------------------------------------------------------------------
def run_command(*args) -> str:
    return subprocess.run(args, stdout=subprocess.PIPE, text=True, check=True).stdout.strip()


# --------------------------------------------------------------------------------------------------
class Git:
    @staticmethod
    def get_current_branch() -> str:
        return run_command("git", "branch", "--show-current")

    @staticmethod
    def get_github_path() -> t.Optional[str]:
        """Retrieve current Git path (<owner>/<repo>)."""
        branch_name = Git.get_current_branch()
        remote_name = run_command("git", "config", f"branch.{branch_name}.remote")
        url = run_command("git", "remote", "get-url", remote_name)
        if match := re.fullmatch(r"(?:git@github\.com:|https://github\.com/)(.*)(?:\.git)?", url):
            return match[1].rstrip('.git')
        print("ERROR - Could not retrieve GibHub branch path")  # noqa: T201
        return None


# --------------------------------------------------------------------------------------------------
class Release(t.TypedDict):
    version: Version
    id: str
    tag: str
    published_at: str


def fetch_github_releases(gh_path: t.Optional[str] = None) -> dict[Package, list[Release]]:
    # Retrieve all available releases (potentially paginating results) for all packages.
    # Returns a dictionary of package_short_name/list-of-releases pairs.
    # A 'release' is a dictionary where "version" if the package version, "id" is the release id and
    # "tag" is the release tag name.
    headers = {"Accept": "application/vnd.github+json"}
    all_releases: dict[str, list[Release]] = {}
    if gh_path is None:
        gh_path = Git.get_github_path()
        if gh_path is None:
            raise ValueError("Couldn't figure out GitHub branch path.")
    url = f"https://api.github.com/repos/{gh_path}/releases"
    page = 1
    # Read all release versions and store them in a package_name - list[Version] dictionary
    while url:
        response = requests.get(url, params={"per_page": 50, "page": page}, headers=headers)
        response.raise_for_status()  # Raise error for bad responses
        for release in response.json():
            release_id = release["id"]
            tag = release["tag_name"]
            published_at = release["published_at"]
            pkg_ver, pkg = tag.split("-") if "-" in tag else (tag, "taipy")
            # Drop legacy packages (config...)
            if pkg != "taipy" and pkg not in Package.NAMES:
                continue

            # Exception for legacy version: v1.0.0 -> 1.0.0
            if pkg_ver == "v1.0.0":
                pkg_ver = pkg_ver[1:]
            version = Version.from_string(pkg_ver)
            new_release: Release = {"version": version, "id": release_id, "tag": tag, "published_at": published_at}
            if releases := all_releases.get(pkg):
                releases.append(new_release)
            else:
                all_releases[pkg] = [new_release]

        # Check for pagination in the `Link` header
        link_header = response.headers.get("Link", "")
        if 'rel="next"' in link_header:
            url = link_header.split(";")[0].strip("<>")  # Extract next page URL
            page += 1
        else:
            url = None  # No more pages

    # Sort all releases for all packages by publishing date (most recent first)
    for p in all_releases.keys():
        all_releases[p].sort(
            key=lambda r: datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")), reverse=True
        )
    # Build and return the dictionary using Package instances
    return {Package(p): v for p, v in all_releases.items()}


# --------------------------------------------------------------------------------------------------
def fetch_latest_github_taipy_releases(
    all_releases: t.Optional[dict[Package, list[Release]]] = None, gh_path: t.Optional[str] = None
) -> Version:
    # Retrieve all available releases if necessary
    if all_releases is None:
        all_releases = fetch_github_releases(gh_path)
    # Find the latest 'taipy' version that has no extension
    latest_taipy_version = Version.UNKNOWN
    releases = all_releases.get(Package("taipy"))
    if releases := all_releases.get(Package("taipy")):
        # Retrieve all non-dev releases
        versions = [release["version"] for release in releases if release["version"].ext is None]
        # Find the latest
        if versions:
            latest_taipy_version = max(versions)
    return latest_taipy_version
