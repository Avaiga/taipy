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


import argparse
import os
import textwrap

from ._main._check_extension import _check_extension
from ._main._generate_tgb import _generate_tgb


def error(message):
    print(message)  # noqa: T201
    exit(1)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="taipy.gui.extension entry point.")
    sub_parser = parser.add_subparsers(dest="command", help="Commands to run", required=True)

    def find_package_root_dir(args) -> str:
        """Finds and validates the package root dir from the command line arguments.

        If args contains no definition for the package root dir look at all subdirectories of the current
        working directory and find the first one that contains a __init__.py file."""
        package_root_dir = args.package_root_dir
        if not package_root_dir:
            # Locate the package root dir from the current working directory
            cwd = os.getcwd()
            for dir_name in os.listdir(cwd):
                path = os.path.join(cwd, dir_name)
                if os.path.isdir(path) and os.path.isfile(os.path.join(path, "__init__.py")):
                    package_root_dir = dir_name
                    break
            if not package_root_dir:
                error("Couldn't find a Python package in the current working directory.")
            print(f"Using directory '{package_root_dir}' as the extension package root dir.")  # noqa: T201
        package_root_dir = str(package_root_dir)
        # Check that the package root dir contains a __init__.py file
        if not os.path.isfile(os.path.join(package_root_dir, "__init__.py")):
            error(f"Directory '{package_root_dir}' is not a Python package (no __init__.py file found).")
        # Remove potential directory separator at the end of the package root dir
        if package_root_dir[-1] == "/" or package_root_dir[-1] == "\\":  # pragma: no cover
            package_root_dir = package_root_dir[:-1]

        return package_root_dir

    def generate_tgb(args) -> int:
        package_root_dir = find_package_root_dir(args)
        return _generate_tgb(package_root_dir, args.output_path, error)

    tgb_generation = sub_parser.add_parser(
        "generate_tgb", aliases=["api"], help="Generate Page Builder API for a Taipy GUI extension package."
    )
    tgb_generation.add_argument(
        dest="package_root_dir",
        nargs="?",
        help=textwrap.dedent("""\
                             The root dir of the extension package.
                             This directory must contain a __init__.py file."""),
    )
    tgb_generation.add_argument(
        dest="output_path",
        nargs="?",
        help=textwrap.dedent("""\
                             The output path for the Python Interface Definition file.
                             The default is a file called '__init__.pyi' in the module's root directory."""),
    )
    tgb_generation.set_defaults(func=generate_tgb)

    # Checking the extension library
    def check_extension(args) -> int:
        package_root_dir = find_package_root_dir(args)
        return _check_extension(package_root_dir, error)

    extension_checker = sub_parser.add_parser("check", help="Check if a Taipy GUI extension package is valid.")
    extension_checker.add_argument(
        dest="package_root_dir",
        nargs="?",
        help=textwrap.dedent("""\
                             The root dir of the extension package.
                             This directory must contain a __init__.py file."""),
    )
    extension_checker.set_defaults(func=check_extension)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    exit(main())
