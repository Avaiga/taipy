import typing as t


def _is_boolean_true(s: t.Union[bool, str]) -> bool:
    return s if isinstance(s, bool) else s.lower() in ["true", "1", "t", "y", "yes", "yeah", "sure"]


def _is_boolean(s: t.Any) -> bool:
    if isinstance(s, bool):
        return True  # pragma: no cover
    elif isinstance(s, str):
        return s.lower() in ["true", "1", "t", "y", "yes", "yeah", "sure", "false", "0", "f", "no"]
    else:
        return False
