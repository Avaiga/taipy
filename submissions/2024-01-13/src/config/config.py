from taipy.config import Config, Scope
import datetime as dt

from algos.algos import add_features, create_train_data, preprocess,\
                        train_arima, train_linear_regression,\
                        forecast, forecast_linear_regression,\
                        concat

#Config.configure_job_executions(mode="standalone", nb_of_workers=2)

path_to_data = "data/covid-19-all.csv"

initial_data_cfg = Config.configure_data_node(id="initial_data",
                                              storage_type="csv",
                                              path=path_to_data,
                                              cacheable=True,
                                              validity_period=dt.timedelta(days=5),
                                              scope=Scope.GLOBAL)

country_cfg = Config.configure_data_node(id="country", default_data="France", 
                                         validity_period=dt.timedelta(days=5))


date_cfg = Config.configure_data_node(id="date", default_data=dt.datetime(2020,10,1),
                                      validity_period=dt.timedelta(days=5))

final_data_cfg =  Config.configure_data_node(id="final_data",
                                             validity_period=dt.timedelta(days=5))

train_data_cfg =  Config.configure_data_node(id="train_data", 
                                             validity_period=dt.timedelta(days=5))

model_arima_cfg = Config.configure_data_node(id="model_arima", validity_period=dt.timedelta(days=5))
model_linear_regression_cfg = Config.configure_data_node(id="model_linear_regression", validity_period=dt.timedelta(days=5))

predictions_arima_cfg = Config.configure_data_node(id="predictions_arima")
predictions_linear_regression_cfg = Config.configure_data_node(id="predictions_linear_regression")

result_cfg = Config.configure_data_node(id="result")


task_preprocess_cfg = Config.configure_task(id="task_preprocess_data",
                                           function=preprocess,
                                           input=[initial_data_cfg, country_cfg, date_cfg],
                                           output=[final_data_cfg,train_data_cfg])


task_train_arima_cfg = Config.configure_task(id="task_train",
                                      function=train_arima,
                                      input=train_data_cfg,
                                      output=model_arima_cfg) 

task_forecast_arima_cfg = Config.configure_task(id="task_forecast",
                                      function=forecast,
                                      input=model_arima_cfg,
                                      output=predictions_arima_cfg)


task_train_linear_regression_cfg = Config.configure_task(id="task_train_linear_regression",
                                      function=train_linear_regression,
                                      input=train_data_cfg,
                                      output=model_linear_regression_cfg)

task_forecast_linear_regression_cfg = Config.configure_task(id="task_forecast_linear_regression",
                                      function=forecast_linear_regression,
                                      input=[model_linear_regression_cfg, date_cfg],
                                      output=predictions_linear_regression_cfg)

task_result_cfg = Config.configure_task(id="task_result",
                                      function=concat,
                                      input=[final_data_cfg, predictions_arima_cfg, predictions_linear_regression_cfg, date_cfg],
                                      output=result_cfg)


scenario_cfg = Config.configure_scenario(id='scenario', task_configs=[task_preprocess_cfg,
                                                                      task_train_arima_cfg,
                                                                      task_forecast_arima_cfg,
                                                                      task_train_linear_regression_cfg,
                                                                      task_forecast_linear_regression_cfg,
                                                                      task_result_cfg])

Config.export('config/config.toml')