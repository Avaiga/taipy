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

from taipy.config.checker.issue import Issue
from taipy.config.checker.issue_collector import IssueCollector


class TestIssueCollector:
    def test_add_error(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector._add_error("field", "value", "message", "checker")
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector._ERROR_LEVEL, "field", "value", "message", "checker")
        collector._add_error("field", "value", "message", "checker")
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector._ERROR_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector._ERROR_LEVEL, "field", "value", "message", "checker")

    def test_add_warning(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector._add_warning("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 0
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector._WARNING_LEVEL, "field", "value", "message", "checker")
        collector._add_warning("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
        assert len(collector.infos) == 0
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector._WARNING_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector._WARNING_LEVEL, "field", "value", "message", "checker")

    def test_add_info(self):
        collector = IssueCollector()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0
        assert len(collector.all) == 0
        collector._add_info("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1
        assert len(collector.all) == 1
        assert collector.all[0] == Issue(IssueCollector._INFO_LEVEL, "field", "value", "message", "checker")
        collector._add_info("field", "value", "message", "checker")
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 2
        assert len(collector.all) == 2
        assert collector.all[0] == Issue(IssueCollector._INFO_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector._INFO_LEVEL, "field", "value", "message", "checker")

    def test_all(self):
        collector = IssueCollector()
        collector._add_info("foo", "bar", "baz", "qux")
        assert collector.all[0] == Issue(IssueCollector._INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector._add_warning("foo2", "bar2", "baz2", "qux2")
        assert collector.all[0] == Issue(IssueCollector._WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[1] == Issue(IssueCollector._INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector._add_warning("foo3", "bar3", "baz3", "qux3")
        assert collector.all[0] == Issue(IssueCollector._WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[1] == Issue(IssueCollector._WARNING_LEVEL, "foo3", "bar3", "baz3", "qux3")
        assert collector.all[2] == Issue(IssueCollector._INFO_LEVEL, "foo", "bar", "baz", "qux")
        collector._add_info("field", "value", "message", "checker")
        collector._add_error("field", "value", "message", "checker")
        assert collector.all[0] == Issue(IssueCollector._ERROR_LEVEL, "field", "value", "message", "checker")
        assert collector.all[1] == Issue(IssueCollector._WARNING_LEVEL, "foo2", "bar2", "baz2", "qux2")
        assert collector.all[2] == Issue(IssueCollector._WARNING_LEVEL, "foo3", "bar3", "baz3", "qux3")
        assert collector.all[3] == Issue(IssueCollector._INFO_LEVEL, "foo", "bar", "baz", "qux")
        assert collector.all[4] == Issue(IssueCollector._INFO_LEVEL, "field", "value", "message", "checker")
