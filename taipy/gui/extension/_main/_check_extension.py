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

import ast
import os
import re
import typing as t
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Message:
    category: str
    status: str  # OK | WARN | FAIL
    message: str
    hint: t.Optional[str] = None


class Results:
    def __init__(self) -> None:
        self.results: t.List[Message] = []

    def ok(self, category: str, msg: str, hint: t.Optional[str] = None) -> None:
        self.results.append(Message(category, "OK", msg, hint))

    def warn(self, category: str, msg: str, hint: t.Optional[str] = None) -> None:
        self.results.append(Message(category, "WARN", msg, hint))

    def fail(self, category: str, msg: str, hint: t.Optional[str] = None) -> None:
        self.results.append(Message(category, "FAIL", msg, hint))

    def test(
        self, condition: bool, ko_status: str, category: str, ok_msg: str, fail_msg: str, hint: t.Optional[str] = None
    ) -> None:
        if condition:
            self.results.append(Message(category, "OK", ok_msg))
        else:
            self.results.append(Message(category, ko_status, fail_msg, hint))

    def render(self) -> int:
        warn_count = sum(1 for r in self.results if r.status == "WARN")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")

        symbols = {"OK": "✔", "WARN": "⚠", "FAIL": "✘"}
        print("Taipy GUI Extension Library - Check Report\n")  # noqa: T201
        for r in self.results:
            sym = symbols.get(r.status, r.status)
            print(f"[{sym} {r.status}] {r.category}: {r.message}")  # noqa: T201
            if r.hint:
                hint_lines = r.hint.splitlines()
                print(f"    hint: {hint_lines[0]}")  # noqa: T201
                for hint_line in hint_lines[1:]:
                    print(f"          {hint_line}")  # noqa: T201

        print(f"\nSummary: {warn_count} warnings, {fail_count} failures.")  # noqa: T201
        return 0 if fail_count == 0 else 1


def _read_text(p: Path) -> t.Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:  # pragma: no cover
        return None


def parse_pyproject(pyproject: str) -> dict[str, t.Optional[str]]:
    name = None
    version = None
    in_project = False
    for raw in pyproject.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            in_project = line.strip() == "[project]"
            continue
        if not in_project:
            continue
        m = re.match(r"name\s*=\s*([\"'])(.+?)\1", line)
        if m:
            name = m.group(2)
            continue
        m = re.match(r"version\s*=\s*([\"'])(.+?)\1", line)
        if m:
            version = m.group(2)
            continue
    return {"name": name, "version": version}


class _LibraryInspector(ast.NodeVisitor):
    def __init__(self, filename: str, libraries: dict[str, dict[str, t.Any]]):
        self.filename = filename
        self.libraries = libraries
        super().__init__()

    def _extract_return_str(self, fn: ast.FunctionDef) -> str:
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                value = stmt.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    return value.value
        return ""  # pragma: no cover

    def _extract_return_list_of_str(self, fn: ast.FunctionDef) -> list[str]:
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                value = stmt.value
                if isinstance(value, ast.List):
                    items: list[str] = []
                    for elt in value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            items.append(elt.value)
                    return items
        return []  # pragma: no cover

    def visit_ClassDef(self, node: ast.ClassDef) -> t.Any:
        if node.bases:
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "ElementLibrary":
                    library: dict[str, t.Any] = {"filename": self.filename}
                    self.libraries[node.name] = library
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "get_name":
                            library["name"] = self._extract_return_str(item)
                        if isinstance(item, ast.FunctionDef) and item.name == "get_scripts":
                            library["scripts"] = self._extract_return_list_of_str(item)
                        if isinstance(item, ast.FunctionDef) and item.name == "get_js_name":
                            library["js_name"] = self._extract_return_str(item)
                        # TODO - get_elements to be checked as well
                        if isinstance(item, ast.FunctionDef) and item.name == "get_elements":
                            library["elements"] = ""  # TODO
                        # - more than one element
                        # - default property present for every element, declared in the element's property dict

        # Continue
        self.generic_visit(node)


def find_extension_libraries(filename: str, file_content: str, libraries: dict[str, dict[str, t.Any]]) -> None:
    abstract_tree = ast.parse(file_content)
    ins = _LibraryInspector(filename, libraries)
    ins.visit(abstract_tree)


def parse_webpack_config(file_content: str) -> dict[str, str]:
    # The proper way would be to use the 'regex' module, that supports recursive patterns:
    # import regex
    #
    # define
    #   BRACES_RE = r"(?(DEFINE)(?P<BLOCK>\{(?:[^{}]++|(?&BLOCK))*\}))"
    # then use that to extract the 'return' object:"
    #   return_re = regex.compile(BRACES_RE + r"return\s*(?P<obj>(?&BLOCK))", FLAGS)
    #   if m := return_re.search(file_content):
    #       config_obj = m.group("obj")
    # config_obj can then be further processed to extract 'entry', 'output', etc.
    #
    # However, we decided to use a simpler approach here because it would otherwise need 'regex' to
    # be added to the dependencies, and enforces its installation in the user's environment.

    # Remove all JS comments from the input text
    FLAGS = re.DOTALL | re.MULTILINE
    file_content = re.sub(r"//.*?$|/\*.*?\*/", "", file_content, flags=FLAGS)

    config: dict[str, str] = {}
    config_obj = ""
    if m := re.search(r"return\s*\{\s*", file_content, flags=FLAGS):
        config_obj = file_content[m.end() :]
    # entry value
    m = re.search(r"entry\s*:\s*\[?['\"](.+?)['\"]\]?", config_obj, FLAGS)
    if m:
        config["entry"] = m.group(1)
    # output settings
    if m := re.search(r"output\s*:\s*\{\s*", config_obj, flags=FLAGS):
        output = config_obj[m.end() :]
        if m := re.search(r"filename\s*:\s*['\"](.+?)['\"]", output, FLAGS):
            config["filename"] = m.group(1)
        if m := re.search(r"path\s*:\s*path\.resolve\(__dirname,\s*['\"](.+?)['\"]\)", output, FLAGS):
            config["path"] = m.group(1)
        # output.library settings
        if m := re.search(r"library\s*:\s*\{\s*", output, FLAGS):
            library = output[m.end() :]
            if m := re.search(r"name\s*:\s*(['\"])(.+?)\1", library, FLAGS):
                config["name"] = m.group(2)
    return config


def _check_extension(package_root_dir: str, _: t.Optional[t.Callable[[str], None]] = None) -> int:  # noqa: C901
    """Check the validity of the extension library package."""

    results = Results()
    top_dir_path = Path(".")
    package_path = Path(package_root_dir)

    # Read and check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.is_file() and (pyproject_text := _read_text(pyproject_path)) is not None:
        pyproject = parse_pyproject(pyproject_text)
        proj_name = pyproject.get("name")
        proj_version = pyproject.get("version")
        if proj_name:
            results.test(
                proj_name == package_root_dir,
                "WARN",
                "pyproject.name",
                f"[project].name='{proj_name}' matches package name.",
                f"[project].name='{proj_name}' differs from package name '{package_root_dir}'.",
                hint="Consider aligning the distribution name with the package name.",
            )
        else:
            results.warn(
                "pyproject.name",
                "pyproject.toml found but [project].name is missing.",
                hint="Add a [project] table with a 'name' key for packaging and distributing the extension library.",
            )
        if proj_version:
            results.ok("pyproject.version", f"Project version: {proj_version}")
    else:
        results.warn(
            "pyproject.toml",
            f"The extension package should contain a 'pyproject.toml' file at its root ('{package_root_dir}').",
            hint="This file is required for packaging and distributing the extension library.",
        )

    # Read MANIFEST.in
    manifest_path = Path("MANIFEST.in")
    manifest_includes = []
    if manifest_path.is_file() and (manifest_text := _read_text(manifest_path)) is not None:
        for line in manifest_text.splitlines():
            s = line.strip()
            if s.startswith("include "):
                manifest_includes.append(s[len("include ") :].strip())
    else:
        results.warn(
            "MANIFEST",
            "MANIFEST.in not found.",
            hint="Create a MANIFEST.in file including your built JS bundle (e.g., "
            + f"'include {package_root_dir}/front-end/dist/*')\n"
            + "for packaging and distributing the extension library.",
        )

    # Find the Library subclass in any module at the root of the package directory
    libraries: dict[str, dict[str, str]] = {}
    main_library_name = None  # TODO - We only consider a single extension library at this point
    for filename in os.listdir(package_root_dir):
        file_content = None
        if filename.endswith(".py") and (file_content := _read_text(package_path / filename)) is not None:
            find_extension_libraries(filename, file_content, libraries)
    if not libraries:  # pragma: no cover
        results.fail(
            "ElementLibrary",
            "No ElementLibrary subclass found in any module at the root of the package directory "
            + f"'{package_root_dir}'.",
            hint="Create an taipy.gui.extension.ElementLibrary subclass to define your extension's elements.",
        )
    else:
        results.ok(
            "ElementLibrary",
            f"Found {len(libraries)} ElementLibrary subclass{'es' if len(libraries) > 1 else ''} in the"
            + f" package directory '{package_root_dir}'.",
        )
        main_library_name = next(iter(libraries.keys()))
        if len(libraries) > 1:  # pragma: no cover
            results.warn(
                "ElementLibrary",
                "Multiple ElementLibrary subclasses found.",
                hint="Extension library checker has limited support for multiple ElementLibrary subclasses.",
            )
    for classname, library in libraries.items():
        if name := library.get("name"):
            results.test(
                name == package_root_dir,
                "WARN",
                "library.name",
                f"Library name '{name}' defined in '{classname}.get_name()' matches package name.",
                f"Library name '{name}' defined in '{classname}.get_name()' differs "
                + f"from package name '{package_root_dir}'.",
                hint="Consider aligning the library name with the package name.",
            )
        else:
            results.fail(
                "library.name",
                f"Library class '{classname}' is missing get_name() implementation.",
                hint="Implement get_name() in your ElementLibrary subclass to return the library name.",
            )
    # Find front-end directory
    frontend_dir_path = None
    for dirpath, dirnames, filenames in os.walk(package_path):
        # Remove any 'temp' directories from traversal
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and d != "node_modules"]

        if "package.json" in filenames:
            frontend_dir_path = Path(dirpath)
            break
    if not frontend_dir_path:
        results.fail(
            "front-end",
            f"No front-end directory found in the package directory '{package_root_dir}'.",
            hint="Create a front-end directory with a 'package.json' file to build your extension's front-end.",
        )
    else:
        results.ok(
            "front-end",
            f"Found front-end directory at '{frontend_dir_path.relative_to(package_path)}'.",
        )

    # Read webpack.config.js
    webpack_config_path = frontend_dir_path / "webpack.config.js" if frontend_dir_path else None
    webpack_config = {}
    if (
        webpack_config_path
        and webpack_config_path.is_file()
        and (webpack_config_text := _read_text(webpack_config_path)) is not None
    ):
        webpack_config = parse_webpack_config(webpack_config_text)
    else:
        results.warn(
            "webpack.config",
            "webpack.config.js not found.",
            hint="Create webpack.config.js in your front-end directory to configure your front-end build process.",
        )

    if "entry" in webpack_config and frontend_dir_path:
        entry_path = frontend_dir_path / webpack_config["entry"]
        results.test(
            entry_path.is_file(),
            "WARN",
            "webpack.entry",
            f"Webpack entry point file found: {entry_path.relative_to(top_dir_path)}",
            f"Webpack entry point file not found: {entry_path.relative_to(top_dir_path)}",
            hint="Check the 'entry' field in your webpack.config.js to ensure it points to a valid file.",
        )
    else:
        results.warn("webpack.entry", "Couldn't verify webpack entry point directory existence.")

    if "name" in webpack_config and frontend_dir_path and main_library_name:
        # NOTE: We only consider the first library found
        if "js_name" in libraries[main_library_name]:
            expected_module_name = libraries[main_library_name]["js_name"]
            results.test(
                webpack_config["name"] == expected_module_name,
                "FAIL",
                "webpack.library.name",
                f"Webpack library name '{expected_module_name}' matches name defined in"
                + f"{main_library_name}.get_js_name().",
                f"Webpack library name '{webpack_config['name']}' does not match "
                + f"the name defined in {main_library_name}.get_js_name() ('{expected_module_name}').",
                hint="Align the webpack library name with the module name defined in"
                + f"{main_library_name}.get_js_name().",
            )
        elif "name" in libraries[main_library_name]:
            expected_module_name = "".join(
                word.capitalize() for word in libraries[main_library_name]["name"].split("_")
            )
            results.test(
                webpack_config["name"] == expected_module_name,
                "FAIL",
                "webpack.library.name",
                f"Webpack library name '{expected_module_name}' matches name derived from "
                + f"{main_library_name}.get_name().",
                f"Webpack library name '{webpack_config['name']}' does not match "
                + f"the name derived from {main_library_name}.get_name() ('{expected_module_name}').",
                hint="Align the webpack library name with the name derived from the name returned by "
                + f"{main_library_name}.get_name().",
            )

    if (
        "filename" in webpack_config
        and frontend_dir_path
        and main_library_name
        and "scripts" in libraries[main_library_name]
    ):
        bundle_dir = "/".join(frontend_dir_path.parts[1:])
        if "path" in webpack_config:
            bundle_dir = os.path.join(bundle_dir, webpack_config["path"])
        bundle_path = os.path.join(bundle_dir, webpack_config["filename"]).replace("\\", "/")
        bundle_dir = os.path.join(package_path, bundle_dir).replace("\\", "/")
        results.test(
            bundle_path in libraries[main_library_name]["scripts"],
            "FAIL",
            "webpack.output",
            f"Webpack output path '{bundle_path}' is returned by {main_library_name}.get_scripts().",
            f"Webpack output path '{bundle_path}' is not returned by {main_library_name}.get_scripts().",
            hint=f"Add '{bundle_path}' to the list returned by {main_library_name}.get_scripts().",
        )
        bundle_path = os.path.join(bundle_dir, webpack_config["filename"]).replace("\\", "/")
        if manifest_includes:
            results.test(
                any(bundle_dir + "/*" == include or bundle_path == include for include in manifest_includes),
                "FAIL",
                "MANIFEST.include",
                f"Webpack output path '{bundle_path}' is included in MANIFEST.in.",
                f"Webpack output path '{bundle_path}' is not included in MANIFEST.in.",
                hint="Include the JS bundle in MANIFEST.in for packaging and distributing the extension library.",
            )

    return results.render()


__all__ = ["_check_extension"]
