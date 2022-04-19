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

from typing import Any, Dict, Union

from taipy.core.config.job_mode_config import _JobModeConfig


class StandaloneConfig(_JobModeConfig):
    """
    Holds configuration fields related to the job executions.

    Properties:
        nb_of_workers (int): The maximum number of running workers to execute jobs. It must be a positive integer.
            The default value is 1.
    """

    _DEFAULT_CONFIG = {
        "nb_of_workers": 1,
    }
