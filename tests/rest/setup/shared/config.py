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

from taipy.common.config import Config, Frequency

from .algorithms import evaluate, forecast

model_cfg = Config.configure_data_node("model", path="my_model.p", storage_type="pickle")

day_cfg = Config.configure_data_node(id="day")
forecasts_cfg = Config.configure_data_node(id="forecasts")
forecast_task_cfg = Config.configure_task(
    id="forecast_task",
    input=[model_cfg, day_cfg],
    function=forecast,
    output=forecasts_cfg,
)

historical_temperature_cfg = Config.configure_data_node(
    "historical_temperature",
    storage_type="csv",
    path="historical_temperature.csv",
    has_header=True,
)
evaluation_cfg = Config.configure_data_node("evaluation")
evaluate_task_cfg = Config.configure_task(
    "evaluate_task",
    input=[historical_temperature_cfg, forecasts_cfg, day_cfg],
    function=evaluate,
    output=evaluation_cfg,
)

scenario_cfg = Config.configure_scenario("scenario", [forecast_task_cfg, evaluate_task_cfg], frequency=Frequency.DAILY)
scenario_cfg.add_sequences({"sequence": [forecast_task_cfg, evaluate_task_cfg]})
