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
    """
    A collection of issues (instances of class `Issue^`).

    Attributes:
        errors (List[Issue^]): List of ERROR issues collected.
        warnings (List[Issue^]): List WARNING issues collected.
        infos (List[Issue^]): List INFO issues collected.
        all (List[Issue^]): List of all issues collected ordered by decreasing level (ERROR, WARNING and INFO).
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
