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
from enum import Enum

import taipy.gui.builder as tgb
from taipy.gui import Gui


# Color values are enumerated
class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


# Initial selected color
# Note that [color] is an enumeration member and [color_value] in a member value
color = Color.RED
color_value = color.value


with tgb.Page() as page:
    tgb.html("h2", "Using enumeration member:")
    tgb.toggle("{color}", lov="{Color}")
    tgb.text("{str(color)}")

    tgb.html("h2", "Using enumeration value:")
    tgb.toggle("{color_value}", lov=Color)
    tgb.text("{color_value}")


if __name__ == "__main__":
    Gui(page).run(title="Binding - LoV as Enum")
