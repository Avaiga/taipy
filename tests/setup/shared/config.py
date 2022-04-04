from taipy.core import Config, Frequency

from .algorithms import *

model_cfg = Config.configure_data_node("model", path="my_model.p", storage_type="pickle")

day_cfg = Config.configure_data_node(id="day")
forecasts_cfg = Config.configure_data_node(id="forecasts")
forecast_task_cfg = Config.configure_task(
    id="forecast_task", input=[model_cfg, day_cfg], function=forecast, output=forecasts_cfg
)

historical_temperature_cfg = Config.configure_data_node(
    "historical_temperature", storage_type="csv", path="historical_temperature.csv", has_header=True
)
evaluation_cfg = Config.configure_data_node("evaluation")
evaluate_task_cfg = Config.configure_task(
    "evaluate_task",
    input=[historical_temperature_cfg, forecasts_cfg, day_cfg],
    function=evaluate,
    output=evaluation_cfg,
)

pipeline_cfg = Config.configure_pipeline("pipeline", [forecast_task_cfg, evaluate_task_cfg])

scenario_cfg = Config.configure_scenario("scenario", [pipeline_cfg], frequency=Frequency.DAILY)
