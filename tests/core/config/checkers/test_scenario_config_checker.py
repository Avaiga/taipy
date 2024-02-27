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

from copy import copy

import pytest

from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from taipy.core.config import ScenarioConfig
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.task_config import TaskConfig


def subtraction(n1, n2):
    return n1 - n2


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
        assert "tasks field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 0

        caplog.clear()

        config._sections[ScenarioConfig.name]["new"].id = "new"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert "tasks field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 0

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

    def test_check_task_configs(self, caplog):
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
        assert "tasks field of ScenarioConfig `new` is empty." in caplog.text
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._tasks = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "tasks field of ScenarioConfig `new` must be populated with a list of"
            ' TaskConfig objects. Current value of property `tasks` is "bar".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._tasks = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "tasks field of ScenarioConfig `new` must be populated with a list of"
            " TaskConfig objects. Current value of property `tasks` is ['bar']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._tasks = ["bar", TaskConfig("bar", print)]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "tasks field of ScenarioConfig `new` must be populated with a list of"
            " TaskConfig objects. Current value of property `tasks` is"
            " ['bar', <taipy.core.config.task_config.TaskConfig object at"
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._tasks = [TaskConfig("bar", print)]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

    def test_check_additional_data_node_configs(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"]._tasks = [TaskConfig("bar", print)]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "additional_data_nodes field of ScenarioConfig `new` must be populated with a list of"
            ' DataNodeConfig objects. Current value of property `additional_data_nodes` is "bar".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "additional_data_nodes field of ScenarioConfig `new` must be populated with a list of"
            " DataNodeConfig objects. Current value of property `additional_data_nodes` is ['bar']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = ["bar", DataNodeConfig("bar")]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "additional_data_nodes field of ScenarioConfig `new` must be populated with a list of"
            " DataNodeConfig objects. Current value of property `additional_data_nodes` is"
            " ['bar', <taipy.core.config.data_node_config.DataNodeConfig object at"
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = [DataNodeConfig("bar")]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

    def test_check_additional_data_node_configs_not_in_task_input_output_data_nodes(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        input_dn_config = DataNodeConfig("input_dn")
        output_dn_config = DataNodeConfig("output_dn")
        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"]._tasks = [
            TaskConfig("bar", print, [input_dn_config], [output_dn_config])
        ]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = [input_dn_config]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 1
        expected_warning_message = (
            "The additional data node `input_dn` in additional_data_nodes field of ScenarioConfig "
            "`new` has already existed as an input or output data node of ScenarioConfig `new` tasks."
        )
        assert expected_warning_message in caplog.text
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = [input_dn_config, output_dn_config]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 2
        expected_warning_message_1 = (
            "The additional data node `input_dn` in additional_data_nodes field of ScenarioConfig "
            "`new` has already existed as an input or output data node of ScenarioConfig `new` tasks."
        )
        expected_warning_message_2 = (
            "The additional data node `output_dn` in additional_data_nodes field of ScenarioConfig "
            "`new` has already existed as an input or output data node of ScenarioConfig `new` tasks."
        )
        assert expected_warning_message_1 in caplog.text
        assert expected_warning_message_2 in caplog.text
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._additional_data_nodes = [DataNodeConfig("bar")]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

    def test_check_tasks_in_sequences_exist_in_scenario_tasks(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        input_dn_config = DataNodeConfig("input_dn")
        output_dn_config = DataNodeConfig("output_dn")
        task_config_1 = TaskConfig("bar", print, [input_dn_config], [output_dn_config])
        task_config_2 = TaskConfig("baz", print, [input_dn_config], [output_dn_config])
        config._sections[ScenarioConfig.name]["new"] = copy(config._sections[ScenarioConfig.name]["default"])
        config._sections[ScenarioConfig.name]["new"]._tasks = [task_config_1]
        config._sections[ScenarioConfig.name]["new"].add_sequences({"sequence_1": [task_config_1]})
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].add_sequences({"sequence_2": ["task_config"]})
        Config._collector = IssueCollector()
        with pytest.raises(SystemExit):
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messgae = (
            "sequences field of ScenarioConfig `new` must be populated with a list of"
            " TaskConfig objects. Current value of property `sequences` is ['task_config']."
        )
        assert expected_error_messgae in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].add_sequences({"sequence_2": [task_config_1, "task_config_2"]})
        Config._collector = IssueCollector()
        with pytest.raises(SystemExit):
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messgae = (
            "sequences field of ScenarioConfig `new` must be populated with a list of"
            " TaskConfig objects. Current value of property `sequences` is ['task_config']."
        )
        assert expected_error_messgae in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].add_sequences({"sequence_2": [task_config_2]})
        Config._collector = IssueCollector()
        with pytest.raises(SystemExit):
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messgae = (
            "The task `baz` in sequences field of ScenarioConfig"
            " `new` must exist in tasks field of ScenarioConfig `new`."
        )
        assert expected_error_messgae in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].add_sequences({"sequence_2": [task_config_1, task_config_2]})
        Config._collector = IssueCollector()
        with pytest.raises(SystemExit):
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messgae = (
            "The task `baz` in sequences field of ScenarioConfig"
            " `new` must exist in tasks field of ScenarioConfig `new`."
        )
        assert expected_error_messgae in caplog.text
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"]._tasks = [task_config_1, task_config_2]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0
        assert len(Config._collector.infos) == 0

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
        assert len(Config._collector.infos) == 0

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
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].frequency = Frequency.DAILY
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0

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
        assert len(Config._collector.infos) == 0

        config._sections[ScenarioConfig.name]["new"].comparators = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "comparators field of ScenarioConfig `new` must be populated with a dictionary value."
            " Current value of property `comparators` is ['bar']."
        )
        assert expected_error_message in caplog.text

        config._sections[ScenarioConfig.name]["new"].comparators = {"bar": 1}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0
        assert len(Config._collector.errors) == 2
        expected_data_node_id_error_message = (
            "The key `bar` in comparators field of ScenarioConfig `new` must be populated with a valid data node"
            " configuration id. Current value of property `comparators` is {'bar': 1}."
        )
        assert expected_data_node_id_error_message in caplog.text
        expected_comparator_error_message = (
            "The value of `bar` in comparators field of ScenarioConfig `new` must be populated with a list of"
            " Callable values. Current value of property `comparators` is {'bar': 1}."
        )
        assert expected_comparator_error_message in caplog.text

        Config.configure_data_node("foo", "in_memory")
        Config.configure_data_node("bar", "in_memory")
        config._sections[ScenarioConfig.name]["new"].comparators = {"bar": 1}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0
        assert len(Config._collector.errors) == 1

        config._sections[ScenarioConfig.name]["new"].comparators = {"foo": subtraction, "bar": [subtraction]}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 1
        assert len(Config._collector.infos) == 0
        assert len(Config._collector.errors) == 0
