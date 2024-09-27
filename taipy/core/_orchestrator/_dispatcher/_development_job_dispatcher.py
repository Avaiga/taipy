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

from typing import Optional

from ...job.job import Job
from .._abstract_orchestrator import _AbstractOrchestrator
from ._job_dispatcher import _JobDispatcher
from ._task_function_wrapper import _TaskFunctionWrapper


class _DevelopmentJobDispatcher(_JobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in a synchronous way."""

    def __init__(self, orchestrator: _AbstractOrchestrator):
        super().__init__(orchestrator)

    def _can_execute(self) -> bool:
        return True

    def start(self):
        raise NotImplementedError

    def is_running(self) -> bool:
        return True

    def stop(self, wait: bool = True, timeout: Optional[float] = None):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        rs = _TaskFunctionWrapper(job.id, job.task).execute()
        self._update_job_status(job, rs)
