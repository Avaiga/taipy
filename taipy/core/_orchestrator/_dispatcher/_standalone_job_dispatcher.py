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

import multiprocessing as mp
from concurrent.futures import Executor, ProcessPoolExecutor
from functools import partial
from threading import Lock
from typing import Callable, Optional

from taipy.common.config import Config
from taipy.common.config._serializer._toml_serializer import _TomlSerializer

from ...job.job import Job
from .._abstract_orchestrator import _AbstractOrchestrator
from ._job_dispatcher import _JobDispatcher
from ._task_function_wrapper import _TaskFunctionWrapper


class _StandaloneJobDispatcher(_JobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in an asynchronous way using a ProcessPoolExecutor."""

    _nb_available_workers_lock = Lock()
    _DEFAULT_MAX_NB_OF_WORKERS = 2

    def __init__(self, orchestrator: _AbstractOrchestrator, subproc_initializer: Optional[Callable] = None):
        super().__init__(orchestrator)
        max_workers = Config.job_config.max_nb_of_workers or self._DEFAULT_MAX_NB_OF_WORKERS
        self._executor: Executor = ProcessPoolExecutor(
            max_workers=max_workers, initializer=subproc_initializer, mp_context=mp.get_context("spawn")
        )
        self._nb_available_workers = self._executor._max_workers  # type: ignore

    def _can_execute(self) -> bool:
        """Returns True if the dispatcher have resources to dispatch a job."""
        with self._nb_available_workers_lock:
            self._logger.debug(f"{self._nb_available_workers=}")
            return self._nb_available_workers > 0

    def run(self):
        with self._executor:
            super().run()
        self._logger.debug("Standalone job dispatcher: Pool executor shut down.")

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        with self._nb_available_workers_lock:
            self._nb_available_workers -= 1
            self._logger.debug(f"Setting nb_available_workers to {self._nb_available_workers} in the dispatch method.")
        config_as_string = _TomlSerializer()._serialize(Config._applied_config)  # type: ignore[attr-defined]

        future = self._executor.submit(_TaskFunctionWrapper(job.id, job.task), config_as_string=config_as_string)
        future.add_done_callback(partial(self._update_job_status_from_future, job))

    def _update_job_status_from_future(self, job: Job, ft):
        with self._nb_available_workers_lock:
            self._nb_available_workers += 1
            self._logger.debug(f"Setting nb_available_workers to {self._nb_available_workers} in the callback method.")
        self._update_job_status(job, ft.result())
