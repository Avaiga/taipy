"""YAML utilities"""

from __future__ import annotations

import yaml
import typing

from apispec.utils import trim_docstring, dedent


def dict_to_yaml(dic: dict, yaml_dump_kwargs: typing.Any | None = None) -> str:
    """Serializes a dictionary to YAML."""
    yaml_dump_kwargs = yaml_dump_kwargs or {}

    # By default, don't sort alphabetically to respect schema field ordering
    yaml_dump_kwargs.setdefault("sort_keys", False)
    return yaml.dump(dic, **yaml_dump_kwargs)


def load_yaml_from_docstring(docstring: str) -> dict:
    """Loads YAML from docstring."""
    split_lines = trim_docstring(docstring).split("\n")

    # Cut YAML from rest of docstring
    for index, line in enumerate(split_lines):
        line = line.strip()
        if line.startswith("---"):
            cut_from = index
            break
    else:
        return {}

    yaml_string = "\n".join(split_lines[cut_from:])
    yaml_string = dedent(yaml_string)
    return yaml.safe_load(yaml_string) or {}


PATH_KEYS = {"get", "put", "post", "delete", "options", "head", "patch"}


def load_operations_from_docstring(docstring: str) -> dict:
    """Return a dictionary of OpenAPI operations parsed from a
    a docstring.
    """
    doc_data = load_yaml_from_docstring(docstring)
    return {
        key: val
        for key, val in doc_data.items()
        if key in PATH_KEYS or key.startswith("x-")
    }
