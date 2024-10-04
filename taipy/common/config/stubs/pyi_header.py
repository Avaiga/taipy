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
import json
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.common.config._config import _Config
from taipy.core.config import CoreSection, DataNodeConfig, JobConfig, ScenarioConfig, TaskConfig

from .checker.issue_collector import IssueCollector
from .common._classproperty import _Classproperty
from .common._config_blocker import _ConfigBlocker
from .common.frequency import Frequency
from .common.scope import Scope
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection
