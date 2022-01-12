from typing import Dict, List

from taipy.common.frequency import Frequency
from taipy.config._config import _Config
from taipy.config.checker.checkers.config_checker import ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.pipeline_config import PipelineConfig
from taipy.config.scenario_config import ScenarioConfig


class ScenarioConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        scenario_configs = self.config.scenarios
        for scenario_config_name, scenario_config in scenario_configs.items():
            self._check_frequency(scenario_config_name, scenario_config)
            self._check_pipelines(scenario_config_name, scenario_config)
            self._check_comparators(scenario_config_name, scenario_config)
        return self.collector

    def _check_pipelines(self, scenario_config_name: str, scenario_config: ScenarioConfig):
        if not scenario_config.pipelines:
            self._warning(
                scenario_config.PIPELINE_KEY,
                scenario_config.pipelines,
                f"{scenario_config.PIPELINE_KEY} field of Scenario {scenario_config_name} is empty.",
            )
        else:
            if not (
                isinstance(scenario_config.pipelines, List)
                and all(map(lambda x: isinstance(x, PipelineConfig), scenario_config.pipelines))
            ):
                self._error(
                    scenario_config.PIPELINE_KEY,
                    scenario_config.pipelines,
                    f"{scenario_config.PIPELINE_KEY} field of Scenario {scenario_config_name} must be populated with a list of Pipeline objects.",
                )

    def _check_frequency(self, scenario_config_name: str, scenario_config: ScenarioConfig):
        if scenario_config.frequency and not isinstance(scenario_config.frequency, Frequency):
            self._error(
                scenario_config.FREQUENCY_KEY,
                scenario_config.frequency,
                f"{scenario_config.FREQUENCY_KEY} field of Scenario {scenario_config_name} must be populated with a Frequency value.",
            )

    def _check_comparators(self, scenario_config_name: str, scenario_config: ScenarioConfig):
        if not scenario_config.comparators:
            self._info(  # TODO: info or warning???
                scenario_config.COMPARATOR_KEY,
                scenario_config.comparators,
                f"{scenario_config.COMPARATOR_KEY} field of Scenario {scenario_config_name} is empty.",
            )
