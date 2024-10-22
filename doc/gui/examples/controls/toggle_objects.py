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
from dataclasses import dataclass

from taipy.gui import Gui


@dataclass
class User:
    id: int
    name: str
    birth_year: int

users = [
    User(231, "Johanna", 1987),
    User(125, "John", 1979),
    User(4,   "Peter", 1968),
    User(31,  "Mary", 1974)
    ]

user_sel = users[2]
page ="""
<|{user_sel}|toggle|lov={users}|type=User|adapter={lambda u: (u.id, u.name)}|>

User: <|{user_sel.name}|>

Born in: <|{user_sel.birth_year}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Toggle - Objects")
