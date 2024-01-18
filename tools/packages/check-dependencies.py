"""
This script is a helper on the dependencies management of the project.
It can be used:
- To check that the same version of a package is set across files.
- To generate a Pipfile from requirements files.
- To display a summary of the dependencies to update.
"""
import sys
import glob
import itertools
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field

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
        if self.extras_dependencies:
            name += f'[{",".join(self.extras_dependencies)}]'
        if without_version:
            if self.installation_markers:
                return f'{name};{self.installation_markers}'
            return name
        if self.installation_markers:
            return f'{name}>={self.min_version},<={self.latest_release.version};{self.installation_markers}'
        return f'{name}>={self.min_version},<={self.latest_release.version}'

    @classmethod
    def check_format(cls, package: str):
        """
        Check if a package definition is correctly formatted.
        """
        if '>=' not in package or '<' not in package:
            # Only Taipy dependencies can be without version.
            if 'taipy' not in package:
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
            is_taipy = 'taipy' in name
            return cls(
                name,
                extract_min_version(package) if not is_taipy else '',
                extract_max_version(package) if not is_taipy else '',
                extract_installation_markers(package) if not is_taipy else '',
                is_taipy,
                extract_extras_dependencies(package),
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
    # The max version is the defined version if it is a fixed version.
    if '==' in package:
        version = package.split('==')[1]
        if ';' in version:
            # Remove installation markers.
            version = version.split(';')[0]
        return version

    return package.split('>=')[1].split(',')[0]


def extract_max_version(package: str) -> str:
    """
    Extract the max version of a package from a requirements line.
    ex: "pandas>=1.0.0,<2.0.0;python_version<'3.9'" -> "2.0.0"
    """
    # The max version is the defined version if it is a fixed version.
    if '==' in package:
        version = package.split('==')[1]
        if ';' in version:
            # Remove installation markers.
            version = version.split(';')[0]
        return version

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
    if '==' in package:
        return package.split('==')[0]

    name = package.split('>=')[0]

    # Remove optional dependencies.
    # Ex: "pandas[sql]" -> "pandas"
    if '[' in name:
        name = name.split('[')[0]
    return name


def extract_extras_dependencies(package: str) -> List[str]:
    """
    Extract the extras dependencies of a package from a requirements line.
    """
    if '[' not in package:
        return []

    return package.split('[')[1].split(']')[0].split(',')


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
                if not existing_package.min_version == package.min_version or \
                    not existing_package.max_version == package.max_version:
                    raise Exception(f"Inconsistent version of '{package.name}' between '{filename}' and {','.join(package.files)}.")

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

        to_print.append((
            package_name,
            f'{package.min_version} ({package.min_release.upload_date if package.min_release else "N.A."})',
            f'{package.max_version} ({package.max_release.upload_date if package.max_release else "N.C."})',
            f'{package.releases[0].version} ({package.releases[0].upload_date})',
            len(list(itertools.takewhile(lambda x: x.version != package.max_version, package.releases))),
        ))

    to_print.sort(key=lambda x: x[0])
    h = ['name', 'version-min', 'version-max', 'current-version', 'nb-releases-behind']
    print(tabulate.tabulate(to_print, headers=h, tablefmt='pretty'))


def dependencies_summary(dependencies_in_use: Dict[str, Package], dependencies_set: Dict[str, Package]):
    """
    Display dependencies to updates.
    """
    to_print = []

    for name, ps in dependencies_set.items():
        if ps.is_taipy:
            continue

        # Find the package in use.
        rp = dependencies_in_use.get(name)
        # Some package as 'gitignore-parser' becomes 'gitignore_parser' during the installation.
        if not rp:
            rp = dependencies_in_use.get(name.replace('-', '_'))

        if rp:
            if rp.max_version != ps.max_version:
                to_print.append((
                    name,
                    rp.max_version,
                    ','.join(f.split('/')[0] for f in ps.files)
                ))

    to_print.sort(key=lambda x: x[0])
    print(tabulate.tabulate(to_print, headers=['name', 'version', 'files'], tablefmt='pretty'))


def generate_raw_requirements_txt(dependencies: Dict[str, Package]):
    """
    Print the dependencies as requirements lines.
    """
    for package in dependencies.values():
        if not package.is_taipy:
            print(package.as_requirements_line(without_version=True))


def update_pipfile(pipfile: str, dependencies_version: Dict[str, Package]):
    """
    Update dependencies version of a Pipfile in place.
    """
    pipfile_obj = toml.load(pipfile)
    for name, dep in pipfile_obj['packages'].items():
        # Find the package in use.
        rp = dependencies_version.get(name)
        # Some package as 'gitignore-parser' becomes 'gitignore_parser' during the installation.
        if not rp:
            rp = dependencies_version.get(name.replace('-', '_'))

        if not rp:
            # Package not found. Can be due to python version.
            # Ex: backports.zoneinfo
            continue

        if isinstance(dep, dict):
            dep['version'] = f'=={rp.max_version}'
        else:
            pipfile_obj['packages'][name] = f'=={rp.max_version}'

    Path(pipfile).write_text(toml.dumps(pipfile_obj), 'UTF-8')


if __name__ == '__main__':
    if sys.argv[1] == 'ensure-same-version':
        # Load dependencies from requirements files.
        # Verify that the same version is set for the same package across files.
        _requirements_filenames = glob.glob('taipy*/*requirements.txt')
        _dependencies = load_dependencies(_requirements_filenames, True)
        display_dependencies_versions(_dependencies)
        sys.exit(0)
    if sys.argv[1] == 'dependencies-summary':
        # Load and compare dependencies from requirements files.
        # The first file is the reference to the other.
        # Display the differences including new version available on Pypi.
        _requirements_filenames = glob.glob('taipy*/*requirements.txt')
        _dependencies_in_use = load_dependencies([sys.argv[2]], False)
        _dependencies_set = load_dependencies(_requirements_filenames, False)
        dependencies_summary(_dependencies_in_use, _dependencies_set)
    if sys.argv[1] == 'generate-raw-requirements':
        # Load dependencies from requirements files.
        # Print the dependencies as requirements lines without born.
        _requirements_filenames = glob.glob('taipy*/*requirements.txt')
        _dependencies = load_dependencies(_requirements_filenames, False)
        generate_raw_requirements_txt(_dependencies)
    if sys.argv[1] == 'generate-pipfile':
        # Generate a new Pipfile from requirements files using dependencies versions
        # set in the requirement file.
        _pipfile_path = sys.argv[2]
        _dependencies_version = load_dependencies([sys.argv[3]], False)
        update_pipfile(_pipfile_path, _dependencies_version)
