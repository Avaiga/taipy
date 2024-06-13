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

import taipy.gui.builder as tgb


# build partial content for a specific data node
def build_dn_partial(dn, dn_label):
    with tgb.Page() as partial_content:
        with tgb.part(render="{selected_scenario}"):
            # ##########################################################################################################
            # PLACEHOLDER: data node specific content before automatic content                                         #
            #                                                                                                          #
            # Example:                                                                                                 #
            if dn_label == "replacement_type":
                tgb.text("All missing values will be replaced by the data node value.")
            # Comment, remove or replace the previous lines with your own use case                                     #
            # ##########################################################################################################

            # Automatic data node content
            tgb.data_node("{selected_scenario.data_nodes['" + dn.config_id + "']}", scenario="{selected_scenario}")

            # ##########################################################################################################
            # PLACEHOLDER: data node specific content after automatic content                                          #
            #                                                                                                          #
            # Example:                                                                                                 #
            if dn_label == "initial_dataset":
                tgb.text("Select your  CSV file:")
                tgb.file_selector(
                    "{selected_data_node.path}",
                    extensions=".csv",
                    on_action="{lambda s: s.refresh('selected_scenario')}",
                )

            # Comment, remove or replace the previous lines with your own use case                                     #
            # ##########################################################################################################

    return partial_content


def manage_partial(state):
    dn = state.selected_data_node
    dn_label = dn.get_simple_label()
    partial_content = build_dn_partial(dn, dn_label)
    state.data_node_partial.update_content(state, partial_content)
