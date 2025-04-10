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
# Increments the patch version number in all the packages' version.json file.
#
# Invoked from the workflow in build-and-release.yml when releasing production packages.
# --------------------------------------------------------------------------------------------------

import argparse

from common import Package, Version


def main():
    parser = argparse.ArgumentParser(description="Increments the patch version number of a package.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    # <package> argument
    def _check_package(value: str) -> str:
        n_value = value.lower()
        if n_value in Package.names(True) or value == "all":
            return n_value
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid Taipy package name.")
    parser.add_argument("package",
                        type=_check_package,
                        action="store",  help="""The name of the package to increment the patch version number.
This should be the short name of a Taipy package (common, core...) or 'taipy'.
If can also be set to 'ALL' then all packages are impacted.
""")
    args = parser.parse_args()

    for package_name in [args.package] if args.package != "all" else Package.names(True):
        package = Package(package_name)
        version = package.load_version()
        if version.ext:
            raise ValueError(f"Package version for '{package.name}' has an extension ({version.full_name}).")
        package.save_version(Version(version.major, version.minor, version.patch + 1))

if __name__ == "__main__":
    main()
