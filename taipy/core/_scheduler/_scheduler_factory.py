# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Type

from taipy.core._scheduler._abstract_scheduler import _AbstractScheduler
from taipy.core._scheduler._scheduler import _Scheduler
from taipy.core.common._utils import _load_fct
from taipy.core.config.config import Config


class _SchedulerFactory:
    @classmethod
    def _build_scheduler(cls) -> Type[_AbstractScheduler]:
        if Config.job_config.is_standalone:
            scheduler = _Scheduler
        else:
            # Mode "airflow" or "enterprise" in the enterprise version
            scheduler = _load_fct(Config.job_config._mode_to_scheduler_path(), "Scheduler")  # type: ignore
        scheduler.initialize()
        return scheduler
