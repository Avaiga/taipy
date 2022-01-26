import typing as t


def is_boolean_true(s: t.Union[bool, str]) -> bool:
    return s if isinstance(s, bool) else s.lower() in ["true", "1", "t", "y", "yes", "yeah", "sure"]
