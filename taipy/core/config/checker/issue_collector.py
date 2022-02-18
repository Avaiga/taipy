from typing import Any, List

from taipy.core.config.checker.issue import Issue


class IssueCollector:
    """
    Dataclass representing an issue detected in the compiled configuration.

    attributes:
        errors (List[Issue]): List of error issues collected.
        warnings (List[Issue]): List warning issues collected.
        infos (List[Issue]): List info issues collected.
        all (List[Issue]): List of all issues collected ordered by decreasing level (Error, warning and info).
    """

    ERROR_LEVEL = "ERROR"
    WARNING_LEVEL = "WARNING"
    INFO_LEVEL = "INFO"

    def __init__(self):
        self.errors: List[Issue] = []
        self.warnings: List[Issue] = []
        self.infos: List[Issue] = []

    @property
    def all(self) -> List[Issue]:
        return self.errors + self.warnings + self.infos

    def add_error(self, field: str, value: Any, message: str, checker_name: str):
        """Adds an issue with error level."""
        self.errors.append(Issue(self.ERROR_LEVEL, field, value, message, checker_name))

    def add_warning(self, field: str, value: Any, message: str, checker_name: str):
        """Adds an issue with warning level."""
        self.warnings.append(Issue(self.WARNING_LEVEL, field, value, message, checker_name))

    def add_info(self, field: str, value: Any, message: str, checker_name: str):
        """Adds an issue with info level."""
        self.infos.append(Issue(self.INFO_LEVEL, field, value, message, checker_name))
