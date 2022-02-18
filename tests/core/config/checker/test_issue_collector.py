from taipy.core.config.checker.issue import Issue
from taipy.core.config.checker.issue_collector import IssueCollector


class TestIssueCollector:
    def test_add_error(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector.add_error("field", "value", "message", "checker")
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector.ERROR_LEVEL, "field", "value", "message", "checker")
        collector.add_error("field", "value", "message", "checker")
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector.ERROR_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector.ERROR_LEVEL, "field", "value", "message", "checker")

    def test_add_warning(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector.add_warning("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 0
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector.WARNING_LEVEL, "field", "value", "message", "checker")
        collector.add_warning("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
        assert len(collector.infos) == 0
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector.WARNING_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector.WARNING_LEVEL, "field", "value", "message", "checker")

    def test_add_info(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector.add_info("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector.INFO_LEVEL, "field", "value", "message", "checker")
        collector.add_info("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 2
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector.INFO_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector.INFO_LEVEL, "field", "value", "message", "checker")

    def test_all(self):
        collector = IssueCollector()
        collector.add_info("foo", "bar", "baz", "qux")
        assert collector.all[0] == Issue(IssueCollector.INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector.add_warning("foo2", "bar2", "baz2", "qux2")
        assert collector.all[0] == Issue(IssueCollector.WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[1] == Issue(IssueCollector.INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector.add_warning("foo3", "bar3", "baz3", "qux3")
        assert collector.all[0] == Issue(IssueCollector.WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[1] == Issue(IssueCollector.WARNING_LEVEL, "foo3", "bar3", "baz3", "qux3")
        assert collector.all[2] == Issue(IssueCollector.INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector.add_info("field", "value", "message", "checker")
        collector.add_error("field", "value", "message", "checker")
        assert collector.all[0] == Issue(IssueCollector.ERROR_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector.WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[2] == Issue(IssueCollector.WARNING_LEVEL, "foo3", "bar3", "baz3", "qux3")
        assert collector.all[3] == Issue(IssueCollector.INFO_LEVEL, "foo", "bar", "baz", "qux")
        assert collector.all[4] == Issue(IssueCollector.INFO_LEVEL, "field", "value", "message", "checker")
