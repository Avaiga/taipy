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

    def __str__(self) -> str:
        message = self.message

        if self.value:
            current_value_str = f'"{self.value}"' if isinstance(self.value, str) else f"{self.value}"
            message += f" Current value of property `{self.field}` is {current_value_str}."

        return message
