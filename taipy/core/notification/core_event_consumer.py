# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from queue import SimpleQueue

from ...common.logger._taipy_logger import _TaipyLogger
from ..common._warnings import _warn_deprecated
from ._core_event_consumer import _CoreEventConsumerBase


class CoreEventConsumerBase(_CoreEventConsumerBase):
    """NOT DOCUMENTED"""

    __logger = _TaipyLogger._get_logger()

    def __init__(self, registration_id: str, queue: SimpleQueue) -> None:
        _warn_deprecated(deprecated="CoreEventConsumerBase",
                         suggest="The 'taipy.event.event_processor.EventProcessor' class")
        self.__logger.warning(
            "The `CoreEventConsumerBase` class is deprecated since taipy 4.1.0. "
            "Please use the `EventProcessor^` class instead."
        )
        super().__init__(registration_id, queue)
