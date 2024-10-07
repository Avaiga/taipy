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
from taipy.gui import Gui, Markdown

# The word provided by the user
word = ""
# A potential error message
error_text = ""
# Is the Validate button enabled?
valid = False
# CSS class to add to control showing a problem
error_cls = None


def on_change(state, var_name, value):
    # If the provided word has changed
    if var_name == "word":
        # If not empty and does not have five characters
        if value and len(value) != 5:
            # Set the error message
            state.error_text = " Five characters are required"
            # Disable the Validate button
            state.valid = False
            # Add the invalid-value class, used by the input control and error message
            state.error_cls = "invalid-value"
        # The text is valid.
        else:
            # Remove error message
            state.error_text = ""
            # Enable the Validate button if the word is not empty
            state.valid = bool(value)
            # Remove the invalid-value class, used by the input control and error message
            state.error_cls = None


page = Markdown(
    """
Enter a five-letter word:
<|{word}|input|class_name={error_cls}|><|{error_text}|text|class_name={error_cls}|>

<|Validate|button|active={valid}|>
""",
    style={".invalid-value": {"background-color": "red"}},
)

if __name__ == "__main__":
    Gui(page).run(title="Styling - Dynamic styling")
