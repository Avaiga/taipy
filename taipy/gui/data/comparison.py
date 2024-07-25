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

import typing as t

import pandas as pd

from .._warnings import _warn
from ..gui import Gui
from ..utils import _getscopeattr


def _compare_function(
    gui: Gui, compare_name: str, name: str, value: pd.DataFrame, datanames: str
) -> t.Optional[pd.DataFrame]:
    try:
        names = datanames.split(",")
        if not names:
            return None
        compare_fn = gui._get_user_function(compare_name) if compare_name else None
        if callable(compare_fn):
            return gui._get_accessor().to_pandas(
                gui._call_function_with_state(compare_fn, [name, [gui._get_real_var_name(n) for n in names]])
            )
        elif compare_fn is not None:
            _warn(f"{compare_name}(): compare function name is not valid.")
        dfs = [gui._get_accessor().to_pandas(_getscopeattr(gui, n)) for n in names]
        return value.compare(dfs[0], keep_shape=True)
    except Exception as e:
        if not gui._call_on_exception(compare_name or "Gui._compare_function", e):
            _warn(f"{compare_name or 'Gui._compare_function'}(): compare function raised an exception", e)
        return None
