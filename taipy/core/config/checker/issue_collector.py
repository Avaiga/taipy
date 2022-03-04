from typing import Any, List

from taipy.core.config.checker.issue import Issue


class IssueCollector:
    """
    A collection of `Issue`s.

    Attributes:
        errors (List[`Issue`]): List of ERROR issues collected.
        warnings (List[`Issue`]): List WARNING issues collected.
        infos (List[`Issue`]): List INFO issues collected.
        all (List[`Issue`]): List of all issues collected ordered by decreasing level (ERROR, WARNING and INFO).
    """

    _ERROR_LEVEL = "ERROR"
    _WARNING_LEVEL = "WARNING"
    _INFO_LEVEL = "INFO"

    def __init__(self):
        self._errors: List[Issue] = []
        self._warnings: List[Issue] = []
        self._infos: List[Issue] = []

    @property
    def all(self) -> List[Issue]:
        return self._errors + self._warnings + self._infos

    @property
    def infos(self) -> List[Issue]:
        return self._infos

    @property
    def warnings(self) -> List[Issue]:
        return self._warnings

    @property
    def errors(self) -> List[Issue]:
        return self._errors

    def _add_error(self, field: str, value: Any, message: str, checker_name: str):
        self._errors.append(Issue(self._ERROR_LEVEL, field, value, message, checker_name))

    def _add_warning(self, field: str, value: Any, message: str, checker_name: str):
        self._warnings.append(Issue(self._WARNING_LEVEL, field, value, message, checker_name))

    def _add_info(self, field: str, value: Any, message: str, checker_name: str):
        self._infos.append(Issue(self._INFO_LEVEL, field, value, message, checker_name))
