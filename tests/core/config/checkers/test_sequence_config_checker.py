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

from copy import copy

import pytest

from src.taipy.core.config.sequence_config import SequenceConfig
from src.taipy.core.config.task_config import TaskConfig
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config


class TestSequenceConfigChecker:
    def test_check_config_id(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[SequenceConfig.name]["new"] = copy(config._sections[SequenceConfig.name]["default"])
        config._sections[SequenceConfig.name]["new"].id = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "config_id of SequenceConfig `None` is empty" in caplog.text
        assert len(Config._collector.warnings) == 1
        assert "tasks field of SequenceConfig `new` is empty." in caplog.text

        caplog.clear()

        config._sections[SequenceConfig.name]["new"].id = "new"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert "tasks field of SequenceConfig `new` is empty." in caplog.text

    def test_check_if_entity_property_key_used_is_predefined(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[SequenceConfig.name]["new"] = copy(config._sections[SequenceConfig.name]["default"])
        config._sections[SequenceConfig.name]["new"]._properties["_entity_owner"] = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "Properties of SequenceConfig `default` cannot have `_entity_owner` as its property." in caplog.text

        config._sections[SequenceConfig.name]["new"] = copy(config._sections[SequenceConfig.name]["default"])
        config._sections[SequenceConfig.name]["new"]._properties["_entity_owner"] = "entity_owner"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "Properties of SequenceConfig `default` cannot have `_entity_owner` as its property."
            ' Current value of property `_entity_owner` is "entity_owner".'
        )
        assert expected_error_message in caplog.text

    def test_check_task(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[SequenceConfig.name]["new"] = copy(config._sections[SequenceConfig.name]["default"])
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert "tasks field of SequenceConfig `new` is empty." in caplog.text

        config._sections[SequenceConfig.name]["new"]._tasks = [TaskConfig("bar", None)]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[SequenceConfig.name]["new"]._tasks = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert len(Config._collector.warnings) == 0
        expected_error_message = (
            "tasks field of SequenceConfig `new` must be populated with a list of TaskConfig"
            ' objects. Current value of property `tasks` is "bar".'
        )
        assert expected_error_message in caplog.text

        config._sections[SequenceConfig.name]["new"]._tasks = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert len(Config._collector.warnings) == 0
        expected_error_message = (
            "tasks field of SequenceConfig `new` must be populated with a list of TaskConfig"
            " objects. Current value of property `tasks` is ['bar']."
        )
        assert expected_error_message in caplog.text
