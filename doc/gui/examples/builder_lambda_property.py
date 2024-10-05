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

persons = {"Albert": 1982, "Beatrix": 1955, "Cecilia": 2003}

current_year = 2024

with tgb.Page() as page:
    tgb.text("Year: ", inline=True)
    tgb.slider("{current_year}", min=1990, max=2050, inline=True)

    for name, birth_year in persons.items():
        tgb.text(lambda current_year: f"{name} would be {current_year-birth_year}")  # noqa: B023

if __name__ == "__main__":
    Gui(page).run(title="Page Builder - Using lambdas in property values")
