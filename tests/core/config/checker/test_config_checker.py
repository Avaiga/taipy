from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.config_checker import ConfigChecker
from taipy.core.config.checker.issue import Issue
from taipy.core.config.checker.issue_collector import IssueCollector


class MyCustomChecker(ConfigChecker):
    def check(self) -> IssueCollector:
        pass


def test__error():
    collector = IssueCollector()
    assert len(collector.all) == 0
    ConfigChecker(_Config(), collector)._error("field", 17, "my message")
    assert len(collector.all) == 1
    assert len(collector.errors) == 1
    assert len(collector.warnings) == 0
    assert len(collector.infos) == 0
    assert collector.errors[0] == Issue(IssueCollector.ERROR_LEVEL, "field", 17, "my message", "ConfigChecker")

    MyCustomChecker(_Config(), collector)._error("foo", "bar", "baz")
    assert len(collector.all) == 2
    assert len(collector.errors) == 2
    assert len(collector.warnings) == 0
    assert len(collector.infos) == 0
    assert collector.errors[0] == Issue(IssueCollector.ERROR_LEVEL, "field", 17, "my message", "ConfigChecker")
    assert collector.errors[1] == Issue(IssueCollector.ERROR_LEVEL, "foo", "bar", "baz", "MyCustomChecker")


def test__warning():
    collector = IssueCollector()
    assert len(collector.all) == 0
    ConfigChecker(_Config(), collector)._warning("field", 17, "my message")
    assert len(collector.all) == 1
    assert len(collector.warnings) == 1
    assert len(collector.errors) == 0
    assert len(collector.infos) == 0
    assert collector.warnings[0] == Issue(IssueCollector.WARNING_LEVEL, "field", 17, "my message", "ConfigChecker")

    MyCustomChecker(_Config(), collector)._warning("foo", "bar", "baz")
    assert len(collector.all) == 2
    assert len(collector.warnings) == 2
    assert len(collector.errors) == 0
    assert len(collector.infos) == 0
    assert collector.warnings[0] == Issue(IssueCollector.WARNING_LEVEL, "field", 17, "my message", "ConfigChecker")
    assert collector.warnings[1] == Issue(IssueCollector.WARNING_LEVEL, "foo", "bar", "baz", "MyCustomChecker")


def test__info():
    collector = IssueCollector()
    assert len(collector.all) == 0
    ConfigChecker(_Config(), collector)._info("field", 17, "my message")
    assert len(collector.all) == 1
    assert len(collector.infos) == 1
    assert len(collector.errors) == 0
    assert len(collector.warnings) == 0
    assert collector.infos[0] == Issue(IssueCollector.INFO_LEVEL, "field", 17, "my message", "ConfigChecker")

    MyCustomChecker(_Config(), collector)._info("foo", "bar", "baz")
    assert len(collector.all) == 2
    assert len(collector.infos) == 2
    assert len(collector.errors) == 0
    assert len(collector.warnings) == 0
    assert collector.infos[0] == Issue(IssueCollector.INFO_LEVEL, "field", 17, "my message", "ConfigChecker")
    assert collector.infos[1] == Issue(IssueCollector.INFO_LEVEL, "foo", "bar", "baz", "MyCustomChecker")
