from taipy.config.checker.checkers.data_node_config_checker import DataNodeConfigChecker
from taipy.config.checker.checkers.gLobal_config_checker import GlobalConfigChecker
from taipy.config.checker.checkers.pipeline_config_checker import PipelineConfigChecker
from taipy.config.checker.checkers.scenario_config_checker import ScenarioConfigChecker
from taipy.config.checker.checkers.task_config_checker import TaskConfigChecker
from taipy.config.checker.issue_collector import IssueCollector


class Checker:
    """holds the various checks to perform on the config."""

    default_checkers = {
        GlobalConfigChecker,
        DataNodeConfigChecker,
        TaskConfigChecker,
        PipelineConfigChecker,
        ScenarioConfigChecker,
    }

    def __init__(self):
        self.checkers = list(self.default_checkers)

    def check(self, _applied_config):
        collector = IssueCollector()
        for checker in self.checkers:
            checker(_applied_config, collector).check()
        return collector
