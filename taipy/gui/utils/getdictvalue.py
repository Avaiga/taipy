from typing import Any


def _get_dict_value(a_dict: dict, name: str) -> Any:
    return a_dict[name] if isinstance(a_dict, dict) and name in a_dict else None
