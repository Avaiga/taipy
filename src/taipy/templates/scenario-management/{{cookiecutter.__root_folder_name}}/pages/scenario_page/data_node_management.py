import re

import pandas as pd


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
    if dn_label == "replacement_type":
        partial_content += "All missing values will be replaced by "
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Automatic data node content
    if dn_content is None:
        partial_content += f"<center> No data for {dn_label}. </center>\n\n"
    elif isinstance(dn_content, pd.DataFrame):
        partial_content += "<|{contents['" + dn.id + "']}|table|rebuild|>\n\n"
    elif (
        isinstance(dn_content, str)
        or isinstance(dn_content, int)
        or isinstance(dn_content, float)
        or isinstance(dn_content, bool)
    ):
        partial_content += "<center> <|{contents['" + dn.id + "']}|input|> </center>\n\n"

    # ##################################################################################################################
    # PLACEHOLDER: data node specific content after automatic content                                                  #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if dn_label == "initial_dataset":
        partial_content += "Select your CSV file: <|{inputs['"
        partial_content += dn.id
        partial_content += "'][2].path}|file_selector|extensions=.csv|>\n\n"
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Default content
    if partial_content == "":
        partial_content += f"<center> No Taipy visual element defined to display data node {dn.id}. </center>\n\n"
    return partial_content


def manage_inputs_partial(state):
    # Update inputs variables and partial
    state.inputs = {d.id: (d.id, d.get_simple_label(), d) for d in state.selected_scenario.get_inputs()}
    state.contents = {k: (v[2].read() if v[2].is_ready_for_reading else None) for k, v in state.inputs.items()}
    input_partial_content = build_dn_list_partial(state.inputs, state.contents)
    state.inputs_partial.update_content(state, input_partial_content)


def manage_outputs_partial(state):
    # Update outputs variables and partial
    state.outputs = {d.id: (d.id, d.get_simple_label(), d) for d in state.selected_scenario.get_outputs()}
    state.contents.update({k: (v[2].read() if v[2].is_ready_for_reading else None) for k, v in state.outputs.items()})
    output_partial_content = build_dn_list_partial(state.outputs, state.contents)
    state.outputs_partial.update_content(state, output_partial_content)


def write_data_nodes(state, var, val):
    CONTENT_VAR_PATTERN = r"contents\['(.*)'\]"
    if match := re.match(CONTENT_VAR_PATTERN, var):
        if match.groups()[0] in state.inputs:
            state.inputs[match.groups()[0]][2].write(val)
        elif match.groups()[0] in state.outputs:
            state.outputs[match.groups()[0]][2].write(val)
        state.selected_scenario = state.selected_scenario


def custom_write_data_nodes(state, var, val):
    # ##################################################################################################################
    # PLACEHOLDER: Add here 'on_change' code to be executed when your own use case variables are modified              #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if match := re.match(r"inputs\['(.*)'\]\[2\].path", var):
        state.inputs[match.groups()[0]][2].path = val
        state.selected_scenario = state.selected_scenario
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################
