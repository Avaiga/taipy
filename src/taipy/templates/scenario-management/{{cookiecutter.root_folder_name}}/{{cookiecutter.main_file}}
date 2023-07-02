import re

import pandas
import taipy as tp
from taipy import Core, Gui
from taipy.gui import navigate

from config.config import configure
from pages import inputs_page
from pages import outputs_page
from pages import root
from pages import scenario_page

selected_scenario = None
inputs = None
outputs = None
contents = None
CONTENT_VAR_PATTERN = r"contents\['(.*)'\]"


def on_init(state):
    state.selected_scenario = None
    state.inputs = {}
    state.outputs = {}
    state.contents = {}


# submit scenario
def submit(scenario):
    scenario.submit()


# check if all scenario inputs are ready to run
def is_ready_to_run(scenario):
    return all([d.is_ready_for_reading for d in scenario._get_inputs()])


# get all scenario inputs
def get_inputs(scenario):
    return {d.id: (d.id, d.get_simple_label(), d) for d in scenario._get_inputs()}


# get all scenario outputs
def get_outputs(scenario):
    data_nodes = scenario.data_nodes.values()
    return {d.id: (d.id, d.get_simple_label(), d) for d in data_nodes if d not in scenario._get_inputs()}


# build partial content for all data nodes
def build_dn_list_partial(dns, dn_contents):
    partial_content = ""
    for dn_id, dn_label, dn in dns.values():
        dn_content = dn_contents.get(dn_id)
        partial_content += f"## {dn_label}\n\n"
        partial_content += build_dn_partial(dn, dn_label, dn_content)
    return partial_content


# build partial content for a specific data node
def build_dn_partial(dn, dn_label, dn_content):
    partial_content = ""

    # ##################################################################################################################
    # PLACEHOLDER: data node specific content before automatic content                                                 #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if dn_label == "replacement_type":                                                                                 #
        partial_content += f"All missing values will be replaced by "                                                  #
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Automatic data node content
    if dn_content is None:
        partial_content += f"<center> No data for {dn_label}. </center>\n\n"
    elif isinstance(dn_content, pandas.DataFrame):
        partial_content += "<|{contents['" + dn.id + "']}|table|>\n\n"
    elif isinstance(dn_content, str) \
            or isinstance(dn_content, int) \
            or isinstance(dn_content, float) \
            or isinstance(dn_content, bool):
        partial_content += "<center> <|{contents['" + dn.id + "']}|input|> </center>\n\n"

    # ##################################################################################################################
    # PLACEHOLDER: data node specific content after automatic content                                                  #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if dn_label == "initial_dataset":                                                                                  #
        partial_content += "Select your CSV file: <|{inputs['"                                                         #
        partial_content += dn.id                                                                                       #
        partial_content += "'][2].path}|file_selector|extensions=.csv|>\n\n"                                           #
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Default content
    if partial_content == "":
        partial_content += f"<center> PLACEHOLDER for a Taipy control for data node {dn.id}. </center>\n\n"
    return partial_content


def on_change(state, var, val):
    if var == "selected_scenario" and val:
        # Update selected scenario
        state.selected_scenario = val

        # Update inputs variables and partial
        state.inputs = get_inputs(state.selected_scenario)
        state.contents = {k: (v[2].read() if v[2].is_ready_for_reading else None) for k, v in state.inputs.items()}
        input_partial_content = build_dn_list_partial(state.inputs, state.contents)
        state.inputs_partial.update_content(state, input_partial_content)

        # Update outputs variables and partial
        state.outputs = get_outputs(state.selected_scenario)
        state.contents.update(
            {k: (v[2].read() if v[2].is_ready_for_reading else None) for k, v in state.outputs.items()})
        output_partial_content = build_dn_list_partial(state.outputs, state.contents)
        state.outputs_partial.update_content(state, output_partial_content)

    elif match := re.match(CONTENT_VAR_PATTERN, var):
        if match.groups()[0] in state.inputs:
            state.inputs[match.groups()[0]][2].write(val)
        elif match.groups()[0] in state.outputs:
            state.outputs[match.groups()[0]][2].write(val)
        state.selected_scenario = state.selected_scenario

    # ##################################################################################################################
    # PLACEHOLDER: Add here 'on_change' code to be executed when your own use case variables are modified              #
    #                                                                                                                  #
    # Example:                                                                                                         #
    elif match := re.match(r"inputs\['(.*)'\]\[2\].path", var):                                                        #
        state.inputs[match.groups()[0]][2].path = val                                                                  #
        state.selected_scenario = state.selected_scenario                                                              #
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################


pages = {"/": root,
         "scenario": scenario_page,
         "inputs": inputs_page,
         "outputs": outputs_page,
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
    if len(tp.get_scenarios()) == 0:                                                                                   #
        tp.create_scenario(default_scenario_cfg, name="Default Scenario")                                              #
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Instantiate, configure and run the GUI
    gui = Gui(pages=pages)
    inputs_partial = gui.add_partial(" <center> Select a Scenario. </center>")
    outputs_partial = gui.add_partial(" <center> Select a Scenario. </center>")
    gui.run(title="{{cookiecutter.application_title}}")
