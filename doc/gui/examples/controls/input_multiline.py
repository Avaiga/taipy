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
from taipy.gui import Gui
import random


def generate_lorem_paragraph(word_count=100):
    words = (
        "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore "
        "magna aliqua"
        "ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat "
        "duis aute irure"
        "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint "
        "occaecat cupidatat non"
        "proident sunt in culpa qui officia deserunt mollit anim id est laborum"
    ).split()

    paragraph = ' '.join(random.choices(words, k=word_count))
    return paragraph


page = """
Multi-line input: <|{generate_lorem_paragraph()}|input|multiline|>
"""

if __name__ == "__main__":
    Gui(page).run()
