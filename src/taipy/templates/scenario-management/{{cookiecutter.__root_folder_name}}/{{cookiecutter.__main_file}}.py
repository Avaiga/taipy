from config.config import configure
from pages import scenario_page
from pages.root import *

import taipy as tp
from taipy import Core, Gui


def on_init(state):
    ...


def on_change(state, var, val):
    state["scenario"].on_change(state, var, val)

    if var == "selected_scenario" and val:
        state.selected_scenario = val  # BUG
        state["scenario"].manage_data_node_partials(state)


pages = {
    "/": root,
    "scenario": scenario_page,
}

if __name__ == "__main__":
    # Instantiate, configure and run the Core
    core = Core()
    default_scenario_cfg = configure()
    core.run()

    # ##################################################################################################################
    # PLACEHOLDER: Initialize your data application here                                                               #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if len(tp.get_scenarios()) == 0:
        tp.create_scenario(default_scenario_cfg, name="Default Scenario")
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Instantiate, configure and run the GUI
    gui = Gui(pages=pages)
    inputs_partial = gui.add_partial("")
    outputs_partial = gui.add_partial("")
    gui.run(title="{{cookiecutter.__application_title}}")
