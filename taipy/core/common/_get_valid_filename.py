import re


class _SuspiciousFileOperation(Exception):
    pass


def _get_valid_filename(name: str) -> str:
    """
    Source: https://github.com/django/django/blob/main/django/utils/text.py
    """
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise _SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)
