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

from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Optional

from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.config import Config

from ...job.job import Job
from .._abstract_orchestrator import _AbstractOrchestrator
from ._job_dispatcher import _JobDispatcher


class _StandaloneJobDispatcher(_JobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in an asynchronous way using a ProcessPoolExecutor."""

    def __init__(self, orchestrator: Optional[_AbstractOrchestrator]):
        super().__init__(orchestrator)
        self._executor = ProcessPoolExecutor(Config.job_config.max_nb_of_workers or 1)  # type: ignore
        self._nb_available_workers = self._executor._max_workers  # type: ignore

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        self._nb_available_workers -= 1

        config_as_string = _TomlSerializer()._serialize(Config._applied_config)
        future = self._executor.submit(self._wrapped_function_with_config_load, config_as_string, job.id, job.task)

        self._set_dispatched_processes(job.id, future)  # type: ignore
        future.add_done_callback(self._release_worker)
        future.add_done_callback(partial(self._update_job_status_from_future, job))

    def _release_worker(self, _):
        self._nb_available_workers += 1

    def _update_job_status_from_future(self, job: Job, ft):
        self._pop_dispatched_process(job.id)  # type: ignore
        self._update_job_status(job, ft.result())
