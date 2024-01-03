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

from unittest.mock import patch

import pytest

from taipy.gui import Gui
from taipy.gui.utils._locals_context import _LocalsContext


def test_locals_context(gui: Gui):
    lc = _LocalsContext()
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        with pytest.raises(KeyError):
            lc.get_default()
        current_locals = locals()
        lc.set_default(current_locals)
        assert lc.get_default() == current_locals
        temp_locals = {"__main__": "test"}
        lc.add("test", temp_locals)
        assert lc.get_context() is None
        assert lc.get_locals() == current_locals
        with lc.set_locals_context("test"):
            assert lc.get_context() == "test"
            assert lc.get_locals() == temp_locals
        assert lc.get_context() is None
        assert lc.get_locals() == current_locals
        assert lc.is_default() is True
        assert "__main__" in lc.get_all_keys()
