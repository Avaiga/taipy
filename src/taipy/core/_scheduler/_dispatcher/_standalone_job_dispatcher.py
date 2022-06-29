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

from concurrent.futures import ProcessPoolExecutor
from functools import partial

from taipy.config import Config

from ._job_dispatcher import _JobDispatcher
from ...job.job import Job


class _StandaloneJobDispatcher(_JobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in an asynchronous way using a ProcessPoolExecutor."""

    def __init__(self):
        super().__init__()
        self._executor = ProcessPoolExecutor(Config.job_config.nb_of_workers or 1)
        self._nb_available_workers = self._executor._max_workers  # type: ignore

    def _can_execute(self) -> bool:
        """Returns True if a worker is available for a new run."""
        return self._nb_available_workers > 0

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        self._nb_available_workers -= 1
        future = self._executor.submit(
            self._run_wrapped_function, Config.global_config.storage_folder, job.id, job.task
        )
        future.add_done_callback(self.__release_worker)
        future.add_done_callback(partial(self._update_status_from_future, job))

    def __release_worker(self, _):
        self._nb_available_workers += 1

    def _update_status_from_future(self, job: Job, ft):
        self._update_status(job, ft.result())
