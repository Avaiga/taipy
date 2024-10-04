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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import builtins
import inspect

from taipy.gui import Gui

# Create a list of Python builtins that:
# - Are callable (i.e. functions)
# - Are not classes (i.e. Exceptions)
# - Do not start with "_" (i.e. internals)
builtin_python_functions = [
    func
    for func in dir(builtins)
    if callable(getattr(builtins, func)) and not inspect.isclass(getattr(builtins, func)) and not func.startswith("_")
]

# Initialize the bound value to the first Python builtin function
selection = builtin_python_functions[0]

page = """
<|{selection}|selector|lov={builtin_python_functions}|filter|multiple|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Selector - Filter")
