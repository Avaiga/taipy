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


class LoadingError(Exception):
    """Raised if an error occurs while loading the configuration file."""


class InconsistentEnvVariableError(Exception):
    """Inconsistency value has been detected in an environment variable referenced by the configuration."""


class MissingEnvVariableError(Exception):
    """Environment variable referenced in configuration is missing."""


class InvalidConfigurationId(Exception):
    """Configuration id is not valid."""


class ConfigurationUpdateBlocked(Exception):
    """The configuration is being blocked from update by other Taipy services."""
