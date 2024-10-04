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

from ..common._repr_enum import _ReprEnum


class Frequency(_ReprEnum):
    """Frequency of the recurrence of `Cycle^` and `Scenario^` objects.

    The frequency must be provided in the `ScenarioConfig^`.

    Each recurrent scenario is attached to the cycle corresponding to the creation date and the
    frequency. In other words, each cycle represents an iteration and contains the various scenarios
    created during this iteration.

    For instance, when scenarios have a _MONTHLY_ frequency, one cycle will be created for each
    month (January, February, March, etc.). A new scenario created on February 10th, gets
    attached to the _February_ cycle.

    The frequency is implemented as an enumeration with the following possible values:

    - With a _DAILY_ frequency, a new cycle is created for each day.

    - With a _WEEKLY_ frequency, a new cycle is created for each week (from Monday to Sunday).

    - With a _MONTHLY_ frequency, a new cycle is created for each month.

    - With a _QUARTERLY_ frequency, a new cycle is created for each quarter.

    - With a _YEARLY_ frequency, a new cycle is created for each year.
    """

    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    QUARTERLY = 4
    YEARLY = 5
