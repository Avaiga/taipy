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

selected_scenario = None
selected_data_node = None


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
