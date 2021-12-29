from taipy.config.checker.checkers.gLobal_config_checker import GlobalConfigChecker
from taipy.config.checker.issue_collector import IssueCollector


class Checker:
    """holds the various checks to perform on the config."""

    default_checkers = {GlobalConfigChecker}

    def __init__(self):
        self.checkers = list(self.default_checkers)

    def check(self, _applied_config):
        collector = IssueCollector()
        for checker in self.checkers:
            checker(_applied_config, collector).check()
        return collector
