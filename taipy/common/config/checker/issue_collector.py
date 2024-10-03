# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Any, List

from .issue import Issue


class IssueCollector:
    """A collection of configuration issues (instances of class `Issue^`).

    `IssueCollector` is a generic class that collects issues detected during the validation
    process. In particular, an `IssueCollector` is created and returned by the `Config.check()^`
    method. It contains all the collected issues separated by severity (ERROR, WARNING, INFO).
    Each issue is an instance of the class `Issue^` and contains the necessary information to
    understand the issue and help the user to fix it.
    """

    _ERROR_LEVEL = "ERROR"
    _WARNING_LEVEL = "WARNING"
    _INFO_LEVEL = "INFO"

    def __init__(self) -> None:
        self._errors: List[Issue] = []
        self._warnings: List[Issue] = []
        self._infos: List[Issue] = []

    @property
    def all(self) -> List[Issue]:
        """List of all issues collected ordered by decreasing level (ERROR, WARNING and INFO)."""
        return self._errors + self._warnings + self._infos

    @property
    def infos(self) -> List[Issue]:
        """List INFO issues collected."""
        return self._infos

    @property
    def warnings(self) -> List[Issue]:
        """List WARNING issues collected."""
        return self._warnings

    @property
    def errors(self) -> List[Issue]:
        """List of ERROR issues collected."""
        return self._errors

    def _add_error(self, field: str, value: Any, message: str, checker_name: str) -> None:
        self._errors.append(Issue(self._ERROR_LEVEL, field, value, message, checker_name))

    def _add_warning(self, field: str, value: Any, message: str, checker_name: str) -> None:
        self._warnings.append(Issue(self._WARNING_LEVEL, field, value, message, checker_name))

    def _add_info(self, field: str, value: Any, message: str, checker_name: str) -> None:
        self._infos.append(Issue(self._INFO_LEVEL, field, value, message, checker_name))
