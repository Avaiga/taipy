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

import random
import string

from example_library import ExampleLibrary

from taipy.gui import Gui

# Initial value
label = "Here is some text"

page = """
# Custom elements example

## Fraction:

No denominator: <|123|example.fraction|>

Denominator is 0: <|321|example.fraction|denominator=0|>

Regular: <|355|example.fraction|denominator=113|>

## Custom label:

Colored text: <|{label}|example.label|>

<|Add a character|button|id=addChar|>
<|Remove a character|button|id=removeChar|>
"""


def on_action(state, id):
    if id == "addChar":
        # Add a random character to the end of 'label'
        state.label += random.choice(string.ascii_letters)
    elif id == "removeChar":
        # Remove the first character of 'label'
        if len(state.label) > 0:
            state.label = state.label[1:]


Gui(page, libraries=[ExampleLibrary()]).run(debug=True)
