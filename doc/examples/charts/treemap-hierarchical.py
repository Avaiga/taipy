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
from taipy.gui import Gui

# Partial family tree of the British House of Windsor
# Source: https://en.wikipedia.org/wiki/Family_tree_of_the_British_royal_family
tree = {
    "name": ["Queen Victoria",
             "Princess Victoria", "Edward VII", "Alice", "Alfred",
             "Wilhelm II",
             "Albert Victor", "George V", "Louise",
             "Ernest Louis",
             "Alfred (2)", "Marie", "Victoria Melita",
             "Edward VIII", "George VI", "Mary",
             "Elizabeth II", "Margaret",
             "Charles III", "Anne", "Andrew",
            ],
    "parent": ["",
               "Queen Victoria", "Queen Victoria", "Queen Victoria", "Queen Victoria",
               "Princess Victoria",
               "Edward VII", "Edward VII", "Edward VII",
               "Alice",
               "Alfred", "Alfred", "Alfred",
               "George V", "George V", "George V",
               "George VI", "George VI",
               "Elizabeth II", "Elizabeth II", "Elizabeth II"
            ]

}

page = """
# TreeMap - Hierarchical

<|{tree}|chart|type=treemap|labels=name|parents=parent|>
"""

Gui(page).run()
