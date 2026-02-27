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

from config.config import configure
from pages import job, scenario

import taipy as tp
import taipy.gui.builder as tgb
from taipy import Gui, Orchestrator
from taipy.gui import State

selected_scenario = None
selected_data_node = None


def on_init(state: State):
    scenario.on_init(state)
    job.on_init(state)


def on_change(state: State, var_name: str, var_value): ...


with tgb.Page() as root:
    with tgb.layout(columns="1 5"):
        with tgb.part(class_name="sidebar"):
            tgb.scenario_selector("{selected_scenario}")

            with tgb.part(render="{selected_scenario}"):
                tgb.data_node_selector("{selected_data_node}", display_cycles=False)

        with tgb.part(class_name="main"):
            tgb.navbar()

            with tgb.part(class_name="main"):
                tgb.content()


pages = {
    "/": root,
    "scenario": scenario.page,
    "jobs": job.page,
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
    gui.run(title="{{cookiecutter.__application_title}}", margin="0em")
