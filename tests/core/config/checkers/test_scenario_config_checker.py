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

from src.taipy.core.config import ScenarioConfig
from src.taipy.core.config.pipeline_config import PipelineConfig
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.frequency import Frequency
from taipy.config.config import Config


class TestScenarioConfigChecker:
    def test_check_config_id(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"].id = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "config_id of ScenarioConfig `None` is empty" in caplog.text
        assert len(Config._collector.warnings) == 1
        assert "pipelines field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 1
        assert "No scenario comparators defined for ScenarioConfig `new`." in caplog.text

        caplog.clear()

        config._sections[ScenarioConfig.name]["new"].id = "new"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert "pipelines field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 1
        assert "No scenario comparators defined for ScenarioConfig `new`." in caplog.text

    def test_check_if_entity_property_key_used_is_predefined(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"]._properties["_entity_owner"] = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "Properties of ScenarioConfig `default` cannot have `_entity_owner` as its property." in caplog.text

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"]._properties["_entity_owner"] = "entity_owner"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "Properties of ScenarioConfig `default` cannot have `_entity_owner` as its property."
            ' Current value of property `_entity_owner` is "entity_owner".'
        )
        assert expected_error_message in caplog.text

    def test_check_pipelines(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert "pipelines field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 1
        assert "No scenario comparators defined for ScenarioConfig `new`." in caplog.text

        config._sections[ScenarioConfig.name]["new"]._pipelines = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "pipelines field of ScenarioConfig `new` must be populated with a list of"
            ' PipelineConfig objects. Current value of property `pipelines` is "bar".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"]._pipelines = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "pipelines field of ScenarioConfig `new` must be populated with a list of"
            " PipelineConfig objects. Current value of property `pipelines` is ['bar']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"]._pipelines = ["bar", PipelineConfig("bar")]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "pipelines field of ScenarioConfig `new` must be populated with a list of"
            " PipelineConfig objects. Current value of property `pipelines` is"
            " ['bar', <src.taipy.core.config.pipeline_config.PipelineConfig object at"
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"]._pipelines = [PipelineConfig("bar")]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 1

    def test_check_frequency(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[ScenarioConfig.name]["default"].frequency = "bar"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        with pytest.raises(SystemExit):
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "frequency field of ScenarioConfig `new` must be populated with a Frequency value."
            ' Current value of property `frequency` is "bar".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"].frequency = 1
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "frequency field of ScenarioConfig `new` must be populated with a Frequency value."
            " Current value of property `frequency` is 1."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"].frequency = Frequency.DAILY
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 1

    def test_check_comparators(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 1

        config._sections[ScenarioConfig.name]["new"].comparators = {"bar": "abc"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0
