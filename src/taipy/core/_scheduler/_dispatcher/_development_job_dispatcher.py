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

from ._standalone_job_dispatcher import _StandaloneJobDispatcher
from .._executor._synchronous import _Synchronous


class _DevelopmentJobDispatcher(_StandaloneJobDispatcher):
    """Manages job dispatching (instances of `Job^` class) in a synchronous way."""

    def __init__(self):
        super().__init__()
        self._executor = _Synchronous()
        self._nb_available_workers = 1
