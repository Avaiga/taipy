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
import taipy.gui.builder as tgb
from taipy.gui import Gui

x_range = range(-10, 11, 4)

data = {"x": x_range, "y": [x * x for x in x_range]}


def even_odd_class(_, row):
    if row % 2:
        # Odd rows are blue
        return "blue-row"
    else:
        # Even rows are red
        return "red-row"


with tgb.Page(
    style={
        ".blue-row>td": {"color": "white", "background-color": "blue"},
        ".red-row>td": {"color": "yellow", "background-color": "red"},
    }
) as page:
    tgb.table("{data}", row_class_name=even_odd_class, show_all=True)
    # Lambda version, getting rid of even_odd_class():
    # tgb.table("{data}", row_class_name=lambda _, row: "blue-row" if row % 2 else "red-row", show_all=True)


if __name__ == "__main__":
    Gui(page).run(title="Table - Styling rows")
