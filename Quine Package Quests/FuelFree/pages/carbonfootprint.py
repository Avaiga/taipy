from taipy.gui import Gui, notify, Markdown

transportation_text = ""
appliances_text = ""
produce_text = ""
approach_text = ""

def on_button_action(state):
    notify(state, 'info', f'Your thoughts are submitted!')
    state.transportation_text = ""
    state.appliances_text = ""
    state.produce_text = ""
    state.approach_text = ""


def on_change(state, var_name, var_value):
    if var_name == "text" and var_value == "Reset":
        state.transportation_text = ""
        state.appliances_text = ""
        state.produce_text = ""
        state.approach_text = ""
        return
    

carbonfootprint_page = Markdown("carbonfootprint.md")