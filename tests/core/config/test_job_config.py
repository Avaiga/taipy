# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest

from src.taipy.config.config import Config


def test_job_config():
    assert Config.job_config.mode == "development"

    job_c = Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    assert job_c.mode == "standalone"
    assert job_c.max_nb_of_workers == 2

    assert Config.job_config.mode == "standalone"
    assert Config.job_config.max_nb_of_workers == 2

    Config.configure_job_executions(foo="bar")
    assert Config.job_config.foo == "bar"


def test_clean_config():
    job_config = Config.configure_job_executions(mode="standalone", max_nb_of_workers=2, prop="foo")

    assert Config.job_config is job_config

    job_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.job_config is job_config

    assert job_config.mode == "development"
    assert job_config._config == {"max_nb_of_workers": 1}
    assert job_config.properties == {}
