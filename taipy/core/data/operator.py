# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from enum import Enum


class Operator(Enum):
    """Enumeration of operators for Data Node filtering.

    The possible values are:

    - `EQUAL`
    - `NOT_EQUAL`
    - `LESS_THAN`
    - `LESS_OR_EQUAL`
    - `GREATER_THAN`
    - `GREATER_OR_EQUAL`
    """

    EQUAL = 1
    NOT_EQUAL = 2
    LESS_THAN = 3
    LESS_OR_EQUAL = 4
    GREATER_THAN = 5
    GREATER_OR_EQUAL = 6


class JoinOperator(Enum):
    """
    Enumeration of join operators for Data Node filtering. The possible values are `AND` and `OR`.
    """

    AND = 1
    OR = 2
