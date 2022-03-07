from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Issue:
    """
    An issue detected in the configuration.

    Attributes:
        level (str): Level of the issue among ERROR, WARNING, INFO.
        field (str): Configuration field on which the issue has been detected.
        value (Any): Value of the field on which the issue has been detected.
        message (str): Human readable message to help the user fix the issue.
        tag (Optional[str]): Optional tag to be used to filter issues.
    """

    level: str
    field: str
    value: Any
    message: str
    tag: Optional[str]
