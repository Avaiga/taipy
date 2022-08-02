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

from .._abstract_scheduler import _AbstractScheduler
from .._executor._synchronous import _Synchronous
from ._standalone_job_dispatcher import _StandaloneJobDispatcher


class _DevelopmentJobDispatcher(_StandaloneJobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in a synchronous way."""

    def __init__(self, scheduler: _AbstractScheduler):
        super().__init__(scheduler)
        self._executor = _Synchronous()  # type: ignore
        self._nb_available_workers = 1

    def start(self):
        return NotImplemented

    def is_running(self) -> bool:
        return True

    def stop(self):
        return NotImplemented
