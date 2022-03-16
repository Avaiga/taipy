from taipy.core import Frequency
import taipy.core as tp

from .algorithms import *

model_cfg = tp.configure_data_node("model", path="my_model.p", storage_type="pickle")

day_cfg = tp.configure_data_node(id="day")
forecasts_cfg = tp.configure_data_node(id="forecasts")
forecast_task_cfg = tp.configure_task(
    id="forecast_task", input=[model_cfg, day_cfg], function=forecast, output=forecasts_cfg
)

historical_temperature_cfg = tp.configure_data_node(
    "historical_temperature", storage_type="csv", path="historical_temperature.csv", has_header=True
)
evaluation_cfg = tp.configure_data_node("evaluation")
evaluate_task_cfg = tp.configure_task(
    "evaluate_task",
    input=[historical_temperature_cfg, forecasts_cfg, day_cfg],
    function=evaluate,
    output=evaluation_cfg,
)

pipeline_cfg = tp.configure_pipeline("pipeline", [forecast_task_cfg, evaluate_task_cfg])

scenario_cfg = tp.configure_scenario("scenario", [pipeline_cfg], frequency=Frequency.DAILY)
