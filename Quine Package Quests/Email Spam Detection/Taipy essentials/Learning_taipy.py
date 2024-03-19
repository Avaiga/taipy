from taipy.gui import Gui, notify

text = "Original text"

# Definition of the page
page = """
# Getting started with Taipy GUI

My text: <|{text}|>

<|{text}|input|>

<|Run local|button|on_action=on_button_action|>
"""

def on_button_action(state):
    notify(state, 'info', f'The text is: {state.text}')
    state.text = "Button Pressed"

def on_change(state, var_name, var_value):
    if var_name == "text" and var_value == "Reset":
        state.text = ""
        return


Gui(page).run(debug=True)