# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
import pytest

import taipy as tp
from taipy import Config
from taipy.core._entity._reload import _Reloader


@pytest.fixture(scope="function", autouse=True)
def reset_reloader():
    """Reset the _Reloader singleton between tests."""
    _Reloader._instance = None
    _Reloader._no_reload_context = False
    _Reloader._context_depth = 0
    yield
    _Reloader._instance = None
    _Reloader._no_reload_context = False
    _Reloader._context_depth = 0


class TestReloader:
    def test_initial_state(self):
        reloader = _Reloader()
        assert reloader._context_depth == 0
        assert not reloader._no_reload_context

    def test_single_context(self):
        dn = tp.create_global_data_node(Config.configure_data_node("dn1", scope=tp.Scope.GLOBAL))
        assert len(dn.edits) == 0
        dn.track_edit(comments="inside") # creates a new edit in memory without saving the data node
        reloader = _Reloader()
        with reloader:
            assert reloader._context_depth == 1
            assert reloader._no_reload_context
            assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
        assert reloader._context_depth == 0
        assert not reloader._no_reload_context
        assert len(dn.edits) == 0 # The dn is reloaded so the edit is removed

    def test_nested_contexts(self):
        dn = tp.create_global_data_node(Config.configure_data_node("dn1", scope=tp.Scope.GLOBAL))
        assert len(dn.edits) == 0
        dn.track_edit(comments="inside") # creates a new edit in memory without saving the data node
        reloader = _Reloader()
        with reloader:
            assert reloader._context_depth == 1
            assert reloader._no_reload_context
            assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
            with reloader:
                assert reloader._context_depth == 2
                assert reloader._no_reload_context
                assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
                with reloader:
                    assert reloader._context_depth == 3
                    assert reloader._no_reload_context
                    assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
                assert reloader._context_depth == 2
                assert reloader._no_reload_context
                assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
            assert reloader._context_depth == 1
            assert reloader._no_reload_context
            assert len(dn.edits) == 1 # The dn is not reloaded so the edit is still there
        assert reloader._context_depth == 0
        assert not reloader._no_reload_context
        assert len(dn.edits) == 0 # The dn is reloaded so the edit is removed

    def test_exception_handling(self):
        reloader = _Reloader()
        try:
            with reloader:
                assert reloader._context_depth == 1
                assert reloader._no_reload_context
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert reloader._context_depth == 0
        assert not reloader._no_reload_context
