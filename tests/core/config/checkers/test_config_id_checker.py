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

import pytest

from taipy.common.config import Config
from taipy.common.config.checker.issue_collector import IssueCollector


class TestConfigIdChecker:
    def test_check_standalone_mode(self, caplog):
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.configure_data_node(id="foo", storage_type="in_memory")
        Config.configure_scenario(id="bar", task_configs=[], additional_data_node_configs=[])

        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        Config.configure_data_node(id="bar", task_configs=[])
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

        expected_error_message = (
            "`bar` is used as the config_id of multiple configurations ['DATA_NODE', 'SCENARIO']"
            ' Current value of property `config_id` is "bar".'
        )
        assert expected_error_message in caplog.text

        Config.configure_task(id="bar", function=print)
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`bar` is used as the config_id of multiple configurations ['DATA_NODE', 'TASK', 'SCENARIO']"
            ' Current value of property `config_id` is "bar".'
        )
        assert expected_error_message in caplog.text

        Config.configure_task(id="foo", function=print)
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        expected_error_message = (
            "`foo` is used as the config_id of multiple configurations ['DATA_NODE', 'TASK']"
            ' Current value of property `config_id` is "foo".'
        )
        assert expected_error_message in caplog.text
