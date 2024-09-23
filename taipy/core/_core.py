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

from taipy.logger._taipy_logger import _TaipyLogger

from .common._warnings import _warn_deprecated
from .orchestrator import Orchestrator


class Core:
    """Deprecated. Use the `Orchestrator^` service class instead."""

    __logger = _TaipyLogger._get_logger()

    def __new__(cls) -> Orchestrator:  # type: ignore
        _warn_deprecated("'Core'", suggest="the 'Orchestrator' class")
        cls.__logger.warning(
            "The `Core` service is deprecated and replaced by the `Orchestrator` service. "
            "An `Orchestrator` instance has been instantiated instead."
        )
        return Orchestrator()
