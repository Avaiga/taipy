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

from concurrent.futures import Executor, Future
from threading import Lock
from typing import List

from taipy.core import Job
from taipy.core._orchestrator._abstract_orchestrator import _AbstractOrchestrator
from taipy.core._orchestrator._dispatcher import _StandaloneJobDispatcher


class MockProcessPoolExecutor(Executor):
    submit_called: List = []
    f: List = []

    def submit(self, fn, *args, **kwargs):
        self.submit_called.append((fn, args, kwargs))
        f = Future()
        try:
            result = fn(*args, **kwargs)
        except BaseException as e:
            f.set_exception(e)
        else:
            f.set_result(result)
        self.f.append(f)
        return f


class MockStandaloneDispatcher(_StandaloneJobDispatcher):
    def __init__(self, orchestrator: _AbstractOrchestrator):
        super(_StandaloneJobDispatcher, self).__init__(orchestrator)
        self._executor: Executor = MockProcessPoolExecutor()
        self._nb_available_workers = 1
        self._nb_available_workers_lock = Lock()

        self.dispatch_calls: List = []
        self.update_job_status_from_future_calls: List = []

    def mock_exception_for_job(self, task_id, e: Exception):
        self.exceptions[task_id] = e  # type: ignore[attr-defined]

    def _dispatch(self, job: Job):
        self.dispatch_calls.append(job)
        super()._dispatch(job)

    def _update_job_status_from_future(self, job: Job, ft):
        self.update_job_status_from_future_calls.append((job, ft))
        super()._update_job_status_from_future(job, ft)
