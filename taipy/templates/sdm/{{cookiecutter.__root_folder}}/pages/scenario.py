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

path_to_uploaded_file = None


def on_init(state: State): ...


def notify_on_submission(state: State, submission: Submission, details: dict):
    if details["submission_status"] == "COMPLETED":
        notify(state, "success", "Submission completed!")
    elif details["submission_status"] == "FAILED":
        notify(state, "error", "Submission failed!")
    else:
        notify(state, "info", "In progress...")


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

        with tgb.part(render="{selected_data_node and selected_scenario}"):
            # ##########################################################################################################
            # PLACEHOLDER: data node specific content before automatic content                                         #
            #                                                                                                          #
            # Example:                                                                                                 #
            with tgb.part(
                render='{selected_data_node and selected_data_node.get_simple_label() == "replacement_type"}'
            ):
                tgb.text("All missing values will be replaced by the data node value.")
            # Comment, remove or replace the previous lines with your own use case                                     #
            # ##########################################################################################################

            # Automatic data node content
            tgb.data_node("{selected_data_node}", scenario="{selected_scenario}")

            # ##########################################################################################################
            # PLACEHOLDER: data node specific content after automatic content                                          #
            #                                                                                                          #
            # Example:                                                                                                 #
            with tgb.part(render='{selected_data_node and selected_data_node.get_simple_label() == "initial_dataset"}'):
                tgb.text("Select your  CSV file:")
                tgb.file_selector(
                    "{path_to_uploaded_file}",
                    extensions=".csv",
                    on_action=lambda s: setattr(s.selected_data_node, "path", s.path_to_uploaded_file),
                )
            # Comment, remove or replace the previous lines with your own use case                                     #
            # ##########################################################################################################
