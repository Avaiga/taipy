# build partial content for a specific data node
def build_dn_partial(dn, dn_label):
    partial_content = "<|part|render={selected_scenario}|\n\n"

    # ##################################################################################################################
    # PLACEHOLDER: data node specific content before automatic content                                                 #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if dn_label == "replacement_type":
        partial_content += "All missing values will be replaced by the data node value."
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    # Automatic data node content
    partial_content += "<|{selected_scenario.data_nodes['" + dn.config_id + "']}|data_node|scenario={selected_scenario}|>\n\n"

    # ##################################################################################################################
    # PLACEHOLDER: data node specific content after automatic content                                                  #
    #                                                                                                                  #
    # Example:                                                                                                         #
    if dn_label == "initial_dataset":
        partial_content += "Select your CSV file: <|{selected_data_node.path}|file_selector|extensions=.csv|>\n\n"
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################

    partial_content += "|>\n\n"
    return partial_content


def manage_partial(state):
    dn = state.selected_data_node
    dn_label = dn.get_simple_label()
    partial_content = build_dn_partial(dn, dn_label)
    state.data_node_partial.update_content(state, partial_content)
