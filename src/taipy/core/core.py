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

from typing import Optional

from ._scheduler._dispatcher._job_dispatcher import _JobDispatcher
from ._scheduler._scheduler import _Scheduler
from ._scheduler._scheduler_factory import _SchedulerFactory


class Core:
    """
    Core service
    """

    _scheduler: Optional[_Scheduler] = None
    _dispatcher: Optional[_JobDispatcher] = None

    def __init__(self):
        """
        Initialize a Core service.
        """
        self._scheduler = _SchedulerFactory._build_scheduler()

    def run(self, force_restart=False):
        """
        Start a Core service. This method is blocking.
        """
        if dispatcher := _SchedulerFactory._build_dispatcher(force_restart=force_restart):
            self._dispatcher = dispatcher
