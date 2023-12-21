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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import numpy
import pandas

from taipy.gui import Gui

# Generate a random value for every hour on a given day
data = {"Date": pandas.date_range("2023-01-04", periods=24, freq="H"), "Value": pandas.Series(numpy.random.randn(24))}

page = """
# Basics - Timeline

<|{data}|chart|x=Date|y=Value|>
"""

Gui(page).run()
