import taipy.gui.builder as tgb
from taipy import Gui

data = {"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1]}

selected = [0]


def num_on_action(state, var_name, payload):
    index = payload.get("index")
    if index in state.selected:
        state.selected = list(set(state.selected) - {index})
    else:
        state.selected = state.selected + [index]


with tgb.Page() as page:
    tgb.toggle(theme=True)

    tgb.table("{data}", selected="{selected}", on_action=num_on_action)

    tgb.table("{data}", selected="{selected}", on_action=num_on_action, class_name="rows-similar rows-bordered")


if __name__ == "__main__":
    gui = Gui(page=page)
    gui.run(run_browser=False, use_reloader=True, port = 5001)