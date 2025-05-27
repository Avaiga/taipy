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

from taipy.gui import Gui
from taipy.gui.utils._evaluator import _Evaluator


def _identity(x):
    return x

def test_evaluate_expr_lambda_from_element(gui: Gui, test_client, helpers):
    gui._Gui__evaluator = _Evaluator({}, []) # type: ignore[attr-defined]
    gui._Gui__locals_context.add("a_module", {"identity": _identity}) # type: ignore[attr-defined]
    with gui._set_locals_context("a_module"):
        evaluated_expr: str = gui._evaluate_expr("lambda x: identity(x)", lambda_expr=True)
        assert evaluated_expr.startswith("__lambda_")
        assert evaluated_expr.endswith("_TPMDL_0")
