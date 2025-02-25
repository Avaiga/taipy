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
"""Configuration of the rest service."""

from taipy.common.config import _inject_section
from taipy.common.config.checker._checker import _Checker

from .rest_checker import _RestConfigChecker
from .rest_config import RestConfig

_inject_section(
    RestConfig,
    "rest",
    RestConfig.default_config(),
    [("configure_rest", RestConfig._configure_rest)]
)

_Checker.add_checker(_RestConfigChecker)
