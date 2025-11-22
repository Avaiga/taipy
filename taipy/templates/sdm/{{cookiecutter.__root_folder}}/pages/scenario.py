# Copyright 2021-2025 Avaiga Private Limited
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
from taipy import DataNode, Submission
from taipy.gui import State, notify


def on_init(state: State): ...


def notify_on_submission(state: State, submission: Submission, details: dict):
    if details["submission_status"] == "COMPLETED":
        notify(state, "success", "Submission completed!")
    elif details["submission_status"] == "FAILED":
        notify(state, "error", "Submission failed!")
    else:
        notify(state, "info", "In progress...")


# build partial content for a specific data node
def build_dn_partial(dn: DataNode, dn_label: str):
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


def manage_data_node_partial(state: State):
    dn = state.selected_data_node
    dn_label = dn.get_simple_label()
    partial_content = build_dn_partial(dn, dn_label)
    state.data_node_partial.update_content(state, partial_content)


with tgb.Page() as page:
    with tgb.layout(columns="1 1"):
        with tgb.part(render="{selected_scenario}"):
            tgb.scenario(
                "{selected_scenario}",
                expandable=False,
                expanded=True,
                on_submission_change=notify_on_submission,
            )

            tgb.scenario_dag("{selected_scenario}")

        tgb.part(partial="{data_node_partial}", render="{selected_data_node}")
