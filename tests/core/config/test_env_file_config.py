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

import os

from taipy.core.config.config import Config
from tests.core.config.named_temporary_file import NamedTemporaryFile


def test_load_from_environment_overwrite_load_from_filename():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
custom_property_not_overwritten = true
custom_property_overwritten = 10
    """
    )
    config_from_environment = NamedTemporaryFile(
        """
[JOB]
custom_property_overwritten = 21
    """
    )

    os.environ[Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    Config.load(config_from_filename.filename)

    assert Config.job_config.custom_property_not_overwritten is True
    assert Config.job_config.custom_property_overwritten == 21
    os.environ.pop(Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH)
