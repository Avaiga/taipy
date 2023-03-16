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

from datetime import datetime
from typing import Callable, List

from taipy.config.common.frequency import Frequency

from ..cycle.cycle import Cycle


class _CycleRepositoryMixin:
    def get_cycles_by_frequency_and_start_date(
        self, frequency: Frequency, start_date: datetime, cycles: List[Cycle]
    ) -> List[Cycle]:
        return self.__get_cycles_cdt(
            lambda cycle: cycle.frequency == frequency and cycle.start_date == start_date, cycles
        )

    def get_cycles_by_frequency_and_overlapping_date(
        self, frequency: Frequency, date: datetime, cycles: List[Cycle]
    ) -> List[Cycle]:
        return self.__get_cycles_cdt(
            lambda cycle: cycle.frequency == frequency and cycle.start_date <= date <= cycle.end_date, cycles
        )

    def __get_cycles_cdt(self, cdt: Callable[[Cycle], bool], cycles: List[Cycle]) -> List[Cycle]:
        return [cycle for cycle in cycles if cdt(cycle)]
