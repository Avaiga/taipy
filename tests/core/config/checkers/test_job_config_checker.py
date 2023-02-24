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

from src.taipy.core.config.job_config import JobConfig
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config


class TestJobConfigChecker:
    def test_check_standalone_mode(self, caplog):
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.configure_data_node(id="foo", storage_type="in_memory")

        Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE, max_nb_of_workers=2)
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=1)
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "DataNode `foo`: In-memory storage type can ONLY be used in development mode. Current"
            ' value of property `storage_type` is "in_memory".'
        )
        assert expected_error_message in caplog.text
