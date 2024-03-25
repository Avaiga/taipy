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

"""
This script is a helper on the dependencies management of the project.
It can be used:
- To check that the same version of a package is set across files.
- To generate a Pipfile and requirements files with the latest version installables.
- To display a summary of the dependencies to update.
"""
import glob
import itertools
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import tabulate
import toml


@dataclass
class Release:
    """
    Information about a release of a package.
    """

    version: str
    upload_date: datetime.date


@dataclass
class Package:
    """
    Information about a package.
    """

    # Package name
    name: str
    # Min version of the package set as requirements.
    min_version: str
    # Max version of the package set as requirements.
    max_version: str
    # Setup installation markers of the package.
    # ex: ;python_version>="3.6"
    installation_markers: str
    # Taipy dependencies are ignored.
    is_taipy: bool
    # Optional dependencies
    extras_dependencies: List[str]
    # Files where the package is set as requirement.
    files: List[str]
    # List of releases of the package.
    releases: List[Release] = field(default_factory=list)
    # Min release of the package.
    # Also present in the releases list.
    min_release: Release = None
    # Max release of the package.
    # Also present in the releases list.
    max_release: Release = None
    # Latest version available on PyPI.
    latest_release: Release = None

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def load_releases(self):
        """
        Retrieve all releases of the package from PyPI.
        """
        import requests  # pylint: disable=import-outside-toplevel

        releases = requests.get(f"https://pypi.org/pypi/{self.name}/json", timeout=5).json().get("releases", {})

        for version, info in releases.items():
            # Ignore old releases without upload time.
            if not info:
                continue
            # Ignore pre and post releases.
            if any(str.isalpha(c) for c in version):
                continue
            date = datetime.strptime(info[0]["upload_time"], "%Y-%m-%dT%H:%M:%S").date()
            release = Release(version, date)
            self.releases.append(release)
            if self.min_version == version:
                self.min_release = release
            # Min and max version can be the same.
            if self.max_version == version:
                self.max_release = release

        self.releases.sort(key=lambda x: x.upload_date, reverse=True)
        self.latest_release = self.releases[0]

    def as_requirements_line(self, with_version: bool = True) -> str:
        """
        Return the package as a requirements line.
        """
        if self.is_taipy:
            return self.name

        name = self.name
        if self.extras_dependencies:
            name += f'[{",".join(self.extras_dependencies)}]'

        if with_version:
            if self.installation_markers:
                return f"{name}>={self.min_version},<={self.max_version};{self.installation_markers}"
            return f"{name}>={self.min_version},<={self.max_version}"

        if self.installation_markers:
            return f"{name};{self.installation_markers}"
        return name

    def as_pipfile_line(self) -> str:
        """
        Return the package as a pipfile line.
        If min_version is True, the min version is used.
        """
        line = f'"{self.name}" = {{version="=={self.max_version}"'

        if self.installation_markers:
            line += f', markers="{self.installation_markers}"'

        if self.extras_dependencies:
            dep = ",".join(f'"{p}"' for p in self.extras_dependencies)
            line += f", extras=[{dep}]"

        line += "}"
        return line

    @classmethod
    def check_format(cls, package: str):
        """
        Check if a package definition is correctly formatted.
        """
        if ">=" not in package or "<" not in package:
            # Only Taipy dependencies can be without version.
            if "taipy" not in package:
                raise Exception(f"Invalid package: {package}")

    @classmethod
    def from_requirements(cls, package: str, filename: str):
        """
        Create a package from a requirements line.
        ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'"
        """
        try:
            # Lower the name to avoid case issues.
            name = extract_name(package).lower()
            is_taipy = "taipy" in name
            return cls(
                name,
                extract_min_version(package) if not is_taipy else "",
                extract_max_version(package) if not is_taipy else "",
                extract_installation_markers(package) if not is_taipy else "",
                is_taipy,
                extract_extras_dependencies(package),
                [filename],
            )
        except Exception as e:
            print(f"Error while parsing package {package}: {e}")  # noqa: T201
            raise


def extract_installation_markers(package: str) -> str:
    """
    Extract the installation markers of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "python_version<'3.9'"
    """
    if ";" not in package:
        return ""
    return package.split(";")[1]


def extract_min_version(package: str) -> str:
    """
    Extract the min version of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "1.0.0"
    """
    # The max version is the defined version if it is a fixed version.
    if "==" in package:
        version = package.split("==")[1]
        if ";" in version:
            # Remove installation markers.
            version = version.split(";")[0]
        return version

    return package.split(">=")[1].split(",")[0]


def extract_max_version(package: str) -> str:
    """
    Extract the max version of a package from a requirements line.
    Ex:
        - pandas==1.0.0 -> 1.0.0
        - pandas>=1.0.0,<=2.0.0 -> 2.0.0
        - pandas==1.0.0;python_version<'3.9' -> 1.0.0
        - pandas>=1.0.0,<2.0.0;python_version<'3.9' -> 2.0.0
    """
    # The max version is the defined version if it is a fixed version.
    if "==" in package:
        version = package.split("==")[1]
        if ";" in version:
            # Remove installation markers.
            version = version.split(";")[0]
        return version

    version = None

    if ",<=" in package:
        version = package.split(",<=")[1]
    else:
        version = package.split(",<")[1]

    if ";" in version:
        # Remove installation markers.
        version = version.split(";")[0]

    return version


def extract_name(package: str) -> str:
    """
    Extract the name of a package from a requirements line.
    Ex:
        - pandas==1.0.0 -> pandas
        - pandas>=1.0.0,<2.0.0 -> pandas
        - pandas==1.0.0;python_version<'3.9' -> pandas
        - pandas>=1.0.0,<2.0.0;python_version<'3.9' -> pandas
    """
    if "==" in package:
        return package.split("==")[0]

    name = package.split(">=")[0]

    # Remove optional dependencies.
    # Ex: "pandas[sql]" -> "pandas"
    if "[" in name:
        name = name.split("[")[0]
    return name


def extract_extras_dependencies(package: str) -> List[str]:
    """
    Extract the extras dependencies of a package from a requirements line.
    Ex:
        - pymongo[srv]>=4.2.0,<=4.6.1 -> ["srv"]
    """
    if "[" not in package:
        return []

    return package.split("[")[1].split("]")[0].split(",")


def load_dependencies(requirements_filenames: List[str], enforce_format: bool) -> Dict[str, Package]:
    """
    Load and concat dependencies from requirements files.
    """
    # Extracted dependencies from requirements files.
    dependencies = {}

    for filename in requirements_filenames:
        file_dependencies = Path(filename).read_text("UTF-8").split("\n")

        for package_requirements in file_dependencies:
            # Ignore empty lines.
            if not package_requirements:
                continue

            # Ensure the package is correctly formatted with born min and max.
            if enforce_format:
                Package.check_format(package_requirements)

            package = Package.from_requirements(package_requirements, filename)

            # dependencies may be present multiple times in different files.
            # In that case, do not load the releases again but ensure versions are the same.
            if package.name in dependencies:
                existing_package = dependencies[package.name]
                if (
                    not existing_package.min_version == package.min_version
                    or not existing_package.max_version == package.max_version
                ):
                    raise Exception(
                        f"Inconsistent version of '{package.name}' between '{filename}' and {','.join(package.files)}."
                    )

                # Add the file as dependency of the package.
                existing_package.files.append(filename)
                # Stop processing, package is already extracted.
                continue

            dependencies[package.name] = package

    return dependencies


def display_dependencies_versions(dependencies: Dict[str, Package]):
    """
    Display dependencies information.
    """
    to_print = []

    for package_name, package in dependencies.items():
        if package.is_taipy:
            continue

        # Load the latest releases of the package.
        package.load_releases()

        to_print.append(
            (
                package_name,
                f'{package.min_version} ({package.min_release.upload_date if package.min_release else "N.A."})',
                f'{package.max_version} ({package.max_release.upload_date if package.max_release else "N.C."})',
                f"{package.releases[0].version} ({package.releases[0].upload_date})",
                len(list(itertools.takewhile(lambda x: x.version != package.max_version, package.releases))),  # noqa: B023
            )
        )

    to_print.sort(key=lambda x: x[0])
    h = ["name", "version-min", "version-max", "current-version", "nb-releases-behind"]
    print(tabulate.tabulate(to_print, headers=h, tablefmt="pretty"))  # noqa: T201


def update_dependencies(
    # Dependencies installed in the environment.
    dependencies_installed: Dict[str, Package],
    # Dependencies set in requirements files.
    dependencies_set: Dict[str, Package],
    # Requirements files to update.
    requirements_filenames: List[str],
):
    """
    Display and updates dependencies.
    """
    to_print = []

    for name, ds in dependencies_set.items():
        if ds.is_taipy:
            continue

        # Find the package in use.
        di = dependencies_installed.get(name)
        # Some package as 'gitignore-parser' becomes 'gitignore_parser' during the installation.
        if not di:
            di = dependencies_installed.get(name.replace("-", "_"))

        if di:
            if di.max_version != ds.max_version:
                to_print.append((name, di.max_version, ",".join(f.split("/")[0] for f in ds.files)))
                # Save the new dependency version.
                ds.max_version = di.max_version

    # Print the dependencies to update.
    to_print.sort(key=lambda x: x[0])
    print(tabulate.tabulate(to_print, headers=["name", "version", "files"], tablefmt="pretty"))  # noqa: T201

    # Update requirements files.
    for fd in requirements_filenames:
        requirements = "\n".join(
            d.as_requirements_line() for d in sorted(dependencies_set.values(), key=lambda d: d.name) if fd in d.files
        )
        # Add a new line at the end of the file.
        requirements += "\n"
        Path(fd).write_text(requirements, "UTF-8")


def generate_raw_requirements_txt(dependencies: Dict[str, Package]):
    """
    Print the dependencies as requirements lines without version.
    """
    for package in dependencies.values():
        if not package.is_taipy:
            print(package.as_requirements_line(with_version=False))  # noqa: T201


def update_pipfile(pipfile: str, dependencies_version: Dict[str, Package]):
    """
    Update in place dependencies version of a Pipfile.
    Warning:
      Dependencies are loaded from requirements files without extras or markers.
      The Pipfile contains extras and markers information.
    """
    dependencies_str = ""
    pipfile_obj = toml.load(pipfile)

    packages = pipfile_obj.pop("packages")
    for name, dep in packages.items():
        # Find the package in use.
        rp = dependencies_version.get(name)
        # Some package as 'gitignore-parser' becomes 'gitignore_parser' during the installation.
        if not rp:
            rp = dependencies_version.get(name.replace("-", "_"))
            if rp:
                # Change for the real name of the package.
                rp.name = name

        if not rp:
            # Package not found. Can be due to python version.
            # Ex: backports.zoneinfo
            if isinstance(dep, dict):
                new_dep = ""
                # Format as a Pipfile line.
                new_dep = f'version="{dep["version"]}"'
                if dep.get("markers"):
                    new_dep += f', markers="{dep["markers"]}"'
                if dep.get("extras"):
                    new_dep += f', extras={dep["extras"]}'
                dep = f"{{{new_dep}}}"
            dependencies_str += f'"{name}" = {dep}\n'
        else:
            if isinstance(dep, dict):
                # Requirements does not have installation markers and extras.
                rp.installation_markers = dep.get("markers", "")
                rp.extras_dependencies = [dep.get("extras")[0]] if dep.get("extras") else []
            dependencies_str += f"{rp.as_pipfile_line()}\n"

    toml_str = toml.dumps(pipfile_obj)
    Path(pipfile).write_text(f"{toml_str}\n\n[packages]\n{dependencies_str}", "UTF-8")


if __name__ == "__main__":
    if sys.argv[1] == "ensure-same-version":
        # Load dependencies from requirements files.
        # Verify that the same version is set for the same package across files.
        _requirements_filenames = glob.glob("taipy*/*requirements.txt")
        _dependencies = load_dependencies(_requirements_filenames, True)
        display_dependencies_versions(_dependencies)
    if sys.argv[1] == "dependencies-summary":
        # Load and compare dependencies from requirements files.
        # The first file is the reference to the other.
        # Display the differences including new version available on Pypi.
        _requirements_filenames = glob.glob("taipy*/*requirements.txt")
        _dependencies_installed = load_dependencies([sys.argv[2]], False)
        _dependencies_set = load_dependencies(_requirements_filenames, False)
        update_dependencies(_dependencies_installed, _dependencies_set, _requirements_filenames)
    if sys.argv[1] == "generate-raw-requirements":
        # Load dependencies from requirements files.
        # Print the dependencies as requirements lines without born.
        _requirements_filenames = glob.glob("taipy*/*requirements.txt")
        _dependencies = load_dependencies(_requirements_filenames, False)
        generate_raw_requirements_txt(_dependencies)
    if sys.argv[1] == "generate-pipfile":
        # Generate a new Pipfile from requirements files using dependencies versions
        # set in the requirement file.
        _pipfile_path = sys.argv[2]
        _dependencies_version = load_dependencies([sys.argv[3]], False)
        update_pipfile(_pipfile_path, _dependencies_version)
