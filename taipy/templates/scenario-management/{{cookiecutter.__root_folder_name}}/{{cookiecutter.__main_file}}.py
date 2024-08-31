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

from config.config import configure
from pages import job_page, scenario_page
from pages.root import content, root, selected_data_node, selected_scenario

import taipy as tp
from taipy import Gui, Orchestrator


def on_init(state):
    ...


def on_change(state, var, val):
    if var == "selected_data_node" and val:
        state["scenario"].manage_data_node_partial(state)


pages = {
    "/": root,
    "scenario": scenario_page,
    "jobs": job_page,
}


if __name__ == "__main__":
    # Instantiate, configure and run the Orchestrator
    orchestrator = Orchestrator()
    default_scenario_cfg = configure()
    orchestrator.run()

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
    data_node_partial = gui.add_partial("")
    gui.run(title="{{cookiecutter.__application_title}}", margin="0em")
