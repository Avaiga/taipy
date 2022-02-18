from taipy.core.config.checker.checkers.data_node_config_checker import DataNodeConfigChecker
from taipy.core.config.checker.checkers.gLobal_config_checker import GlobalConfigChecker
from taipy.core.config.checker.checkers.job_config_checker import JobConfigChecker
from taipy.core.config.checker.checkers.pipeline_config_checker import PipelineConfigChecker
from taipy.core.config.checker.checkers.scenario_config_checker import ScenarioConfigChecker
from taipy.core.config.checker.checkers.task_config_checker import TaskConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector


class Checker:
    """holds the various checks to perform on the config."""

    default_checkers = {
        GlobalConfigChecker,
        DataNodeConfigChecker,
        TaskConfigChecker,
        PipelineConfigChecker,
        ScenarioConfigChecker,
        JobConfigChecker,
    }

    def __init__(self):
        self.checkers = list(self.default_checkers)

    def check(self, _applied_config):
        collector = IssueCollector()
        for checker in self.checkers:
            checker(_applied_config, collector).check()
        return collector
