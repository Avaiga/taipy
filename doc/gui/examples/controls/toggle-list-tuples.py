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
from taipy.gui import Gui, Icon
from taipy.gui import builder as tgb

lov = [
    ("id1", "Label 1"),
    ("id2", Icon("https://docs.taipy.io/en/latest/assets/images/favicon.png", "Taipy Logo"), "Label 2"),
    ("id3", "Label 3"),
]
value = lov[0]

with tgb.Page() as page:
    tgb.toggle("{value}", lov="{lov}")  # type: ignore[attr-defined]
    tgb.html(None, "Value: ")
    tgb.text("{value[1].text if isinstance(value[1], Icon) else value[1]}", inline=True)  # type: ignore[attr-defined]


if __name__ == "__main__":
    Gui(page).run(title="Toggle - List tuples")
