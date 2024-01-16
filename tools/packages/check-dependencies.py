"""
Display and update in place packages versions in requirements files.

Usage:
    # Update in place requirements files.
    python tools/packages/check-dependencies.py ensure-same-version tools/packages/taipy-core/setup.requirements.txt tools/packages/taipy/setup.requirements.txt tools/packages/taipy-gui/setup.requirements.txt tools/packages/taipy-config/setup.requirements.txt tools/packages/taipy-rest/setup.requirements.txt
    # Update in place requirements files and update the pipfile.
    python tools/packages/manager.py pipfile tools/packages/taipy-core/setup.requirements.txt tools/packages/taipy/setup.requirements.txt tools/packages/taipy-gui/setup.requirements.txt tools/packages/taipy-config/setup.requirements.txt tools/packages/taipy-rest/setup.requirements.txt
"""
import sys
from typing import List, Dict
import requests
import itertools
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

import toml
import tabulate


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
    # Taipy packages are ignored.
    is_taipy: bool
    # Optional packages
    extras_packages: List[str]
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
        releases = requests.get(
            f"https://pypi.org/pypi/{self.name}/json",
            timeout=5
        ).json().get('releases', {})

        for version, info in releases.items():
            # Ignore old releases without upload time.
            if not info:
                continue
            # Ignore pre and post releases.
            if any(str.isalpha(c) for c in version):
                continue
            date = datetime.strptime(info[0]['upload_time'], "%Y-%m-%dT%H:%M:%S").date()
            release = Release(version, date)
            self.releases.append(release)
            if self.min_version == version:
                self.min_release = release
            # Min and max version can be the same.
            if self.max_version == version:
                self.max_release = release

        self.releases.sort(key=lambda x: x.upload_date, reverse=True)
        self.latest_release = self.releases[0]

    def as_requirements_line(self, without_version: bool) -> str:
        """
        Return the package as a requirements line.
        """
        if self.is_taipy:
            return self.name

        name = self.name
        if self.extras_packages:
            name += f'[{",".join(self.extras_packages)}]'
        if without_version:
            return f'{name};{self.installation_markers}'
        if self.installation_markers:
            return f'{name}>={self.min_version},<={self.latest_release.version};{self.installation_markers}'
        return f'{name}>={self.min_version},<={self.latest_release.version}'

    def as_pipfile_line(self, min_version=True) -> str:
        """
        Return the package as a pipfile line.
        If min_version is True, the min version is used.
        """
        if self.is_taipy:
            version = self.latest_release.version
        else:
            version = self.min_version if min_version else self.max_version
        line = f'"{self.name}" = {{version="<={version}"'

        if self.installation_markers:
            line += f', markers="{self.installation_markers}"'

        if self.extras_packages:
            packages = ','.join(f'"{p}"' for p in self.extras_packages)
            line += f', extras=[{packages}]'

        line += '}'
        return line

    @classmethod
    def check_format(cls, package: str):
        """
        Check if a package definition is correctly formatted.
        """
        if '>=' not in package or '<' not in package:
            # Only Taipy packages can be without version.
            if 'taipy' not in package:
                raise Exception(f"Invalid package: {package}")

    @classmethod
    def from_requirements(cls, package: str, filename: str):
        """
        Create a package from a requirements line.
        ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'"
        """
        try:
            name = extract_name(package)
            is_taipy = 'taipy' in name
            return cls(
                name,
                extract_min_version(package) if not is_taipy else '',
                extract_max_version(package) if not is_taipy else '',
                extract_installation_markers(package) if not is_taipy else '',
                is_taipy,
                extract_extras_packages(package),
                [filename]
            )
        except Exception as e:
            print(f"Error while parsing package {package}: {e}")
            raise


def extract_installation_markers(package: str) -> str:
    """
    Extract the installation markers of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "python_version<'3.9'"
    """
    if ';' not in package:
        return ''
    return package.split(';')[1]


def extract_min_version(package: str) -> str:
    """
    Extract the min version of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "1.0.0"
    """
    return package.split('>=')[1].split(',')[0]


def extract_max_version(package: str) -> str:
    """
    Extract the max version of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "2.0.0"
    """
    version = None

    if ',<=' in package:
        version = package.split(',<=')[1]
    else:
        version = package.split(',<')[1]

    if ';' in version:
        # Remove installation markers.
        version = version.split(';')[0]

    return version


def extract_name(package: str) -> str:
    """
    Extract the name of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "pandas"
    """
    name = package.split('>=')[0]

    # Remove optional dependencies.
    # Ex: "pandas[sql]" -> "pandas"
    if '[' in name:
        name = name.split('[')[0]
    return name


def extract_extras_packages(package: str) -> List[str]:
    """
    Extract the extras packages of a package from a requirements line.
    """
    if '[' not in package:
        return []

    return package.split('[')[1].split(']')[0].split(',')


def load_packages(requirements_filenames: List[str]) -> Dict[str, Package]:
    """
    Load and concat packages from requirements files.
    """
    # Extracted packages from requirements files.
    packages = {}

    for filename in requirements_filenames:
        file_packages = Path(filename).read_text("UTF-8").split("\n")

        for package_requirements in file_packages:
            # Ignore empty lines.
            if not package_requirements:
                continue

            Package.check_format(package_requirements)
            package = Package.from_requirements(package_requirements, filename)

            # Packages may be present multiple times in different files.
            # In that case, do not load the releases again but ensure versions are the same.
            if package.name in packages:
                existing_package = packages[package.name]
                if not existing_package.min_version == package.min_version or \
                    not existing_package.max_version == package.max_version:
                    raise Exception(f"Package {package.name} is present twice but differently")

                # Add the file as dependency of the package.
                existing_package.files.append(filename)
                # Stop processing, package is already extracted.
                continue

            packages[package.name] = package

    return packages


def display_packages_versions(packages: Dict[str, Package]):
    """
    Display packages information.
    """
    to_print = []

    for package_name, package in packages.items():
        if package.is_taipy:
            continue

        # Load the latest releases of the package.
        package.load_releases()

        to_print.append((
            package_name,
            f'{package.min_version} ({package.min_release.upload_date if package.min_release else "N.A."})',
            f'{package.max_version} ({package.max_release.upload_date if package.max_release else "N.C."})',
            f'{package.releases[0].version} ({package.releases[0].upload_date})',
            len(list(itertools.takewhile(lambda x: x.version != package.max_version, package.releases))),
        ))

    h = ['name', 'version-min', 'version-max', 'current-version', 'nb-releases-behind']
    print(tabulate.tabulate(to_print, headers=h, tablefmt='pretty'))


def packages_to_updates(targetted_version: Dict[str, Package], current_packages: Dict[str, Package]):
    """
    Display dependencies to updates.
    """
    # Sort packages by name to ensure they will be the same during iteration.
    _targetted_version = sorted(targetted_version.values(), key=lambda x: x.name)
    _current_packages = sorted(current_packages.values(), key=lambda x: x.name)

    to_print = []
    for tpackage, cpackage in zip(_targetted_version, _current_packages):
        if tpackage.max_version != cpackage.max_version:
            to_print.append((
                tpackage.name,
                tpackage.max_version,
                ",".join(cpackage.files)
            ))

    print(tabulate.tabulate(to_print, headers=['name', 'version', 'files'], tablefmt='pretty'))


def display_raw_packages(packages: Dict[str, Package]):
    for package in packages.values():
        print(package.as_requirements_line(without_version=True))


def update_pipfile(packages: Dict[str, Package], pipfile: str):
    pipfile_obj = toml.load(pipfile)
    del pipfile_obj['packages']
    toml_str = toml.dumps(pipfile_obj)
    packages_str = "\n".join(p.as_pipfile_line(min_version=True) for p in packages.values())
    Path(pipfile).write_text(f'{toml_str}\n\n[packages]\n{packages_str}', 'UTF-8')


if __name__ == '__main__':
    if sys.argv[1] == 'ensure-same-version':
        _packages = load_packages(sys.argv[2: len(sys.argv)])
        display_packages_versions(_packages)
        sys.exit(0)
    if sys.argv[1] == 'dependencies-to-update':
        _version_targetted = load_packages([sys.argv[2]])
        _current_packages = load_packages(sys.argv[3: len(sys.argv)])
        packages_to_updates(_version_targetted, _current_packages)
    if sys.argv[1] == 'raw-packages':
        _packages = load_packages(sys.argv[2: len(sys.argv)])
        display_raw_packages(_packages)
