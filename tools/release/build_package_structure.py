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
# Builds the structure to hold the package files.
#
# Invoked by the workflow files build-and-release-single-package.yml and build-and-release.yml.
# Working directory must be '[checkout-root]'.
# --------------------------------------------------------------------------------------------------
import argparse
import json
import os
import re
import shutil
from pathlib import Path

from common import Package, Version

# Base build directory name
DEST_ROOT = "build_"

# Files to be copied from taipy/<package> to build directory
BUILD_CP_FILES = ["README.md", "setup.py"]

# Files to be moved from taipy/<package> to build directory
BUILD_MV_FILES = ["LICENSE", "package_desc.md", "pyproject.toml"]

# Items to skip while copying directory structure
SKIP_ITEMS = {
    "taipy": [
        "build_taipy",
        "doc",
        "frontend",
        "tests",
        "tools",
        ".git",
        ".github",
        ".pytest_cache",
        "node_modules",
    ],
    "taipy-gui": [
        "node_modules",
    ],
}

# Regexp identifying subpackage directories in taipy hierarchy
packages = "|".join(Package.NAMES)
SUB_PACKAGE_DIR_PATTERN = re.compile(rf"taipy/(?:{packages})")


# Filters files not to be copied
def skip_path(path: str, package: Package, parent: str) -> bool:
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    # Specific items per package
    if (skip_items := SKIP_ITEMS.get(package.short_name, None)) and path in skip_items:
        return True
    # Taipy sub-package directories
    if package.name == "taipy" and SUB_PACKAGE_DIR_PATTERN.fullmatch(path):
        return True
    # Others
    if path.endswith("__pycache__") or path.startswith("build_"):
        return True
    return False


def recursive_copy(package: Package, source, dest, *, parent: str = "", skip_root: bool = False):
    dest_path = dest if skip_root else os.path.join(dest, os.path.basename(source))
    if not skip_root:
        os.makedirs(dest_path, exist_ok=True)

    for item in os.listdir(source):
        src_item = os.path.join(source, item)
        dest_item = os.path.join(dest_path, item)
        if not skip_path(src_item, package, parent):
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dest_item)
            elif os.path.isdir(src_item):
                if (s := src_item.replace("\\", "/")).startswith("./"):
                    s = s[2:]
                recursive_copy(package, src_item, dest_path, parent=s)


def main():
    parser = argparse.ArgumentParser(
        description="Creates the directory structure to build a Taipy package.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "package",
        type=Package.check_argument,
        action="store",
        help="""The name of the package to setup the build version for.
This must be the short name of a Taipy package (common, core...) or 'taipy'.
""",
    )
    parser.add_argument("version", type=Version.check_argument, action="store", help="Version of the package to build.")
    args = parser.parse_args()
    package = Package(args.package)

    if package.name == "taipy":
        # Check that gui_core bundle was built
        if not os.path.exists("taipy/gui_core/lib/taipy-gui-core.js"):
            raise SystemError("Taipy GUI-Core bundle was not built")
    elif package.name == "gui":
        # Check that gui bundle was built
        if not os.path.exists("taipy/gui/webapp/taipy-gui.js"):
            raise SystemError("Taipy GUI bundle was not built")

    # Create 'build_<package>' target directory and its subdirectory 'taipy' if needed
    build_dir = Path(DEST_ROOT + package.short_name)
    if build_dir.exists():
        print(f"Removing legacy directory '{build_dir}'")  # noqa: T201
        shutil.rmtree(build_dir)
    dest_dir = build_dir
    if package.name != "taipy":
        dest_dir = build_dir / "taipy"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy the package build files from taipy[/package] to build_<package>/taipy
    recursive_copy(package, "." if package.name == "taipy" else package.package_dir, dest_dir)

    # This is needed for local builds (i.e. not in a Github workflow)
    if package.name == "taipy":
        # Needs the frontend build scripts
        tools_dir = build_dir / "tools" / "frontend"
        tools_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2("tools/frontend/bundle_build.py", tools_dir)
        # Copy the build files from tools/packages/taipy to build_taipy
        recursive_copy(package, Path("tools") / "packages" / "taipy", build_dir, skip_root=True)
    else:
        build_package_dir = build_dir / package.package_dir
        # Copy build files from package to build dir
        for filename in BUILD_CP_FILES:
            shutil.copy2(build_package_dir / filename, build_dir)
        # Move build files from package to build dir
        for filename in BUILD_MV_FILES:
            shutil.move(build_package_dir / filename, build_dir)
        # Copy the build files from tools/packages/taipy-<package> to build_<package>
        recursive_copy(package, Path("tools") / "packages" / f"taipy-{package.short_name}", build_dir, skip_root=True)

    # Check that versions were set in setup.requirements.txt
    with open(build_dir / "setup.requirements.txt") as requirements_file:
        for line in requirements_file:
            if match := re.fullmatch(r"(taipy\-\w+)(.*)", line.strip()):
                if not match[2]:  # Version not updated
                    print(f"setup.requirements.txt not up-to-date in 'tools/packages/{package.short_name}'.")  # noqa: T201
                    raise SystemError(f"Version for dependency on {match[1]} is missing.")
    # Update package's version.json
    with open(build_dir / package.package_dir / "version.json", "w") as version_file:
        json.dump(args.version.to_dict(), version_file)

    # Copy topmost __init__
    if package.name != "taipy":
        shutil.copy2(Path("taipy") / "__init__.py", dest_dir)


if __name__ == "__main__":
    main()
