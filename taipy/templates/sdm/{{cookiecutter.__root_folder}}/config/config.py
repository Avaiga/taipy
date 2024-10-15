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

from algos import clean_data

from taipy.common.config import Config, Frequency, Scope


def configure():
    # ##################################################################################################################
    # PLACEHOLDER: Add your scenario configurations here                                                               #
    #                                                                                                                  #
    # Example:                                                                                                         #
    initial_dataset_cfg = Config.configure_csv_data_node("initial_dataset", scope=Scope.CYCLE)
    replacement_type_cfg = Config.configure_data_node("replacement_type", default_data="NO VALUE")
    cleaned_dataset_cfg = Config.configure_csv_data_node("cleaned_dataset")
    clean_data_cfg = Config.configure_task(
        "clean_data",
        function=clean_data,
        input=[initial_dataset_cfg, replacement_type_cfg],
        output=cleaned_dataset_cfg,
    )
    scenario_cfg = Config.configure_scenario(
        "scenario_configuration", task_configs=[clean_data_cfg], frequency=Frequency.DAILY
    )
    return scenario_cfg
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################
