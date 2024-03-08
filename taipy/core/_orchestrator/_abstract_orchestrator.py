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

from abc import abstractmethod
from typing import Callable, Iterable, Optional, Union

from .._entity.submittable import Submittable
from ..job.job import Job
from ..submission.submission import Submission
from ..task.task import Task


class _AbstractOrchestrator:
    """Creates, enqueues, and orchestrates jobs as instances of `Job^` class."""

    @property
    @abstractmethod
    def jobs_to_run(self):
        pass

    @property
    @abstractmethod
    def blocked_jobs(self):
        pass

    @classmethod
    @abstractmethod
    def initialize(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def submit(
        cls,
        submittable: Submittable,
        callbacks: Optional[Iterable[Callable]],
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        **properties,
    ) -> Submission:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def submit_task(
        cls,
        task: Task,
        callbacks: Optional[Iterable[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        **properties,
    ) -> Submission:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def cancel_job(cls, job: Job):
        raise NotImplementedError
