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
