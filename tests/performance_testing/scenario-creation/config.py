# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime as dt

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from taipy.config import Config
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope

group_info = {
    "Toto": {
        "groupe": "Toto",
        "anneeHist": 2019,
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "montantFidelite": str([0, 0, 0, 0]),
        "montantRemiseConditionnelle": str([0, 0, 0, 0]),
    },
    "Quux": {
        "groupe": "Quux",
        "anneeHist": 2019,
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "ristourneCompensee": str([0, 0, 0, 0]),
    },
    "Something": {"groupe": "Something", "anneeHist": 2020, "taux": str([0.0, 0.0, 0.0, 0.0])},
    "Plugh": {"groupe": "Plugh", "anneeHist": 2020, "taux": str([0.0, 0.0, 0.0, 0.0])},
    "Tata": {"groupe": "Tata", "anneeHist": 2019, "taux": str([0.0, 0.0, 0.0, 0.0])},
    "Quuz": {"groupe": "Quuz", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "titi": {
        "groupe": "titi",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "ristourneCompensee": str([0, 0, 0, 0]),
    },
    "Tutu": {"groupe": "Tutu", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "Grault": {"groupe": "Grault", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "Waldo": {"groupe": "Waldo", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "Foo": {"groupe": "Foo", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "Bar": {"groupe": "Bar", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2019},
    "Qux": {"groupe": "Qux", "taux": str([0.0, 0.0, 0.0, 0.0]), "anneeHist": 2020},
    "Baz": {
        "groupe": "Baz",
        "anneeHist": 2019,
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "Corge": {
        "groupe": "Corge",
        "anneeHist": 2019,
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "xyzzy": {
        "groupe": "xyzzy",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "Garply": {
        "groupe": "Garply",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "Fred": {
        "groupe": "Fred",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "Babble": {
        "groupe": "Babble",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "montantAjustement": str([0, 0, 0, 0]),
    },
    "Thud": {
        "groupe": "Thud",
        "taux": str([0.0, 0.0, 0.0, 0.0]),
        "anneeHist": 2019,
        "montantAjustement": str([0, 0, 0, 0]),
    },
}

groups = list(group_info.keys())

signed_column = [
    "groupe Baseline",
    "groupe Min Baseline",
    "groupe Max Baseline",
    "groupe ML",
    "groupe Min ML",
    "groupe Max ML",
    "Historique",
]


def predict(parameters):
    group = parameters["groupe"]
    print(f" - Predicting {group}")
    return "raw_predictions"


def convert_predictions(raw_predictions, parameters):
    group = parameters["groupe"]
    print(f" - Converting predictions {group}")

    debut_date = parameters["debutDate"]
    length_of_predictions = len(raw_predictions[0][group])

    data_range = pd.Series(
        pd.date_range(debut_date, periods=length_of_predictions, freq="D", tz="UTC"),
        name="Date",
        index=[str(i) for i in range(length_of_predictions)],
    )
    data_range = data_range.apply(lambda x: x.to_datetime64())

    for i in range(len(raw_predictions)):
        if raw_predictions[i]["Algo"]["isBaseline"]:
            metadata_baseline = raw_predictions[i]["Algo"]

            group_baseline = pd.Series(raw_predictions[i][group], name=group + " Baseline")
            group_min_baseline = pd.Series(raw_predictions[i][group + "_min"], name=group + " Min Baseline")
            group_max_baseline = pd.Series(raw_predictions[i][group + "_max"], name=group + " Max Baseline")

        else:
            metadata_ml = raw_predictions[i]["Algo"]
            group_ml = pd.Series(raw_predictions[i][group], name=group + " ML")
            group_min_ml = pd.Series(raw_predictions[i][group + "_min"], name=group + " Min ML")
            group_max_ml = pd.Series(raw_predictions[i][group + "_max"], name=group + " Max ML")

    predictions = pd.concat(
        [data_range, group_baseline, group_min_baseline, group_max_baseline, group_ml, group_min_ml, group_max_ml],
        axis=1,
    )

    print(predictions)
    return predictions, [metadata_baseline, metadata_ml]


def aggregate_predictions(
    Toto,
    Quux,
    Something,
    Plugh,
    Tata,
    Quuz,
    titi,
    Tutu,
    Grault,
    Waldo,
    Foo,
    Bar,
    Qux,
    Baz,
    Corge,
    xyzzy,
    Garply,
    Fred,
    Babble,
    Thud,
):
    print(" - Aggregating predictions")

    df_aggregated = pd.DataFrame(
        {
            "Date": [],
            "groupe Baseline": [],
            "groupe Min Baseline": [],
            "groupe Max Baseline": [],
            "groupe ML": [],
            "groupe Min ML": [],
            "groupe Max ML": [],
            "groupe": [],
        }
    )

    dfs = [
        Toto,
        Quux,
        Something,
        Plugh,
        Tata,
        Quuz,
        titi,
        Tutu,
        Grault,
        Waldo,
        Foo,
        Bar,
        Qux,
        Baz,
        Corge,
        xyzzy,
        Garply,
        Fred,
        Babble,
        Thud,
    ]

    for df in dfs:
        groupe = df.columns[1].split(" ")[0]
        df.columns = [
            "Date",
            "groupe Baseline",
            "groupe Min Baseline",
            "groupe Max Baseline",
            "groupe ML",
            "groupe Min ML",
            "groupe Max ML",
        ]
        df["groupe"] = [groupe] * len(df)
        df_aggregated = pd.concat([df_aggregated, df], axis=0, ignore_index=True)

    df_aggregated["Date"] = df_aggregated["Date"].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    return df_aggregated


def convert_raw_history(raw_historical_data):
    print(" - Converting historical data")
    print(raw_historical_data.columns)

    raw_historical_data.drop(columns=["CODE_SENS"], inplace=True)

    raw_historical_data.columns = ["groupe", "Date", "Historique"]

    raw_historical_data["Date"] = raw_historical_data["Date"].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    print(raw_historical_data)
    return raw_historical_data


def aggregate_historic(dataset_predictions, historical_data):
    print(" - Aggregating historical data")

    full_dataset_pred = pd.merge(dataset_predictions, historical_data, on=["groupe", "Date"], how="outer")
    full_dataset_pred = full_dataset_pred[full_dataset_pred["groupe ML"].notnull()]
    full_dataset_pred.reset_index(drop=True, inplace=True)
    return full_dataset_pred


def reform_dataset(full_dataset, reformist):
    print(" - Reform dataset")
    for i in range(len(reformist)):
        date = reformist["Date"][i]
        groupe = reformist["groupe"][i]
        index = (full_dataset["Date"].apply(lambda x: x.date()) == date) & (full_dataset["groupe"] == groupe)
        if sum(index) > 0:
            # full_dataset["groupe ML"][index] = reformist["value ML"][i] # += > =
            full_dataset["groupe Baseline"][index] = reformist["value Baseline"][i]  # += > =
        else:
            print(" - Warning: no prediction for {} {}".format(groupe, date))

    return full_dataset


def create_metrics(full_dataset, horizon, historical_data):  #
    print("- Creating metrics")
    metrics = pd.DataFrame(
        {
            "groupe": [],
            "Absolute Baseline MAE": [],
            "Absolute ML MAE": [],
            "Absolute Baseline RMSE": [],
            "Absolute ML RMSE": [],
            "Absolute Baseline Bias": [],
            "Absolute ML Bias": [],
            "Relative Baseline MAE": [],
            "Relative ML MAE": [],
            "Relative Baseline RMSE": [],
            "Relative ML RMSE": [],
            "Relative Baseline Bias": [],
            "Relative ML Bias": [],
        }
    )

    full_dataset_no_nan = full_dataset[full_dataset["Historique"].notnull()]

    if len(full_dataset_no_nan) > 0:
        new_horizon = min((full_dataset_no_nan["Date"].max() - full_dataset_no_nan["Date"].min()).days + 1, horizon)
        full_dataset_no_nan = full_dataset_no_nan[
            (full_dataset_no_nan["Date"] < (full_dataset_no_nan["Date"][0] + dt.timedelta(days=new_horizon)))
        ]

        for groupe in full_dataset_no_nan["groupe"].unique():
            groupe_data = full_dataset_no_nan[full_dataset_no_nan["groupe"] == groupe]
            groupe_data = groupe_data.sort_values(by="Date")
            groupe_historical_data = historical_data[historical_data["groupe"] == groupe]

            absolute_baseline_mae = mean_absolute_error(groupe_data["groupe Baseline"], groupe_data["Historique"])
            absolute_ml_mae = mean_absolute_error(groupe_data["groupe ML"], groupe_data["Historique"])
            absolute_baseline_rmse = np.sqrt(
                mean_squared_error(groupe_data["groupe Baseline"], groupe_data["Historique"])
            )
            absolute_ml_rmse = np.sqrt(mean_squared_error(groupe_data["groupe ML"], groupe_data["Historique"]))
            absolute_baseline_bias = np.abs(np.mean(groupe_data["groupe Baseline"] - groupe_data["Historique"]))
            absolute_ml_bias = np.abs(np.mean(groupe_data["groupe ML"] - groupe_data["Historique"]))

            relative_baseline_mae = mean_absolute_error(
                groupe_data["groupe Baseline"], groupe_data["Historique"]
            ) / np.mean(groupe_historical_data["Historique"])
            relative_ml_mae = mean_absolute_error(groupe_data["groupe ML"], groupe_data["Historique"]) / np.mean(
                groupe_historical_data["Historique"]
            )
            relative_baseline_rmse = np.sqrt(
                mean_squared_error(groupe_data["groupe Baseline"], groupe_data["Historique"])
            ) / np.mean(groupe_historical_data["Historique"])
            relative_ml_rmse = np.sqrt(
                mean_squared_error(groupe_data["groupe ML"], groupe_data["Historique"])
            ) / np.mean(groupe_historical_data["Historique"])
            relative_baseline_bias = np.abs(
                np.mean(groupe_data["groupe Baseline"] - groupe_data["Historique"])
                / np.mean(groupe_historical_data["Historique"])
            )
            relative_ml_bias = np.abs(
                np.mean(groupe_data["groupe ML"] - groupe_data["Historique"])
                / np.mean(groupe_historical_data["Historique"])
            )

            new_line = pd.DataFrame(
                {
                    "groupe": [groupe],
                    "Absolute Baseline MAE": [absolute_baseline_mae],
                    "Absolute ML MAE": [absolute_ml_mae],
                    "Absolute Baseline RMSE": [absolute_baseline_rmse],
                    "Absolute ML RMSE": [absolute_ml_rmse],
                    "Absolute Baseline Bias": [absolute_baseline_bias],
                    "Absolute ML Bias": [absolute_ml_bias],
                    "Relative Baseline MAE": [relative_baseline_mae],
                    "Relative ML MAE": [relative_ml_mae],
                    "Relative Baseline RMSE": [relative_baseline_rmse],
                    "Relative ML RMSE": [relative_ml_rmse],
                    "Relative Baseline Bias": [relative_baseline_bias],
                    "Relative ML Bias": [relative_ml_bias],
                }
            )

            metrics = pd.concat([metrics, new_line], axis=0, ignore_index=True)

        temp = full_dataset_no_nan.copy()
        for col in signed_column:
            temp[col] = temp[col] * (1 - 2 * temp["groupe"].str.startswith("Dec"))
        temp = temp.drop(["groupe"], axis=1).groupby(by="Date").sum()
        temp.insert(0, "Date", temp.index)
        temp = temp.reset_index(drop=True)

        groupe_data = temp.sort_values(by="Date")

        temp = historical_data.copy()
        temp["Historique"] = temp["Historique"] * (1 - 2 * temp["groupe"].str.startswith("Dec"))
        temp = temp.drop(["groupe"], axis=1).groupby(by="Date").sum()
        temp.insert(0, "Date", temp.index)
        temp = temp.reset_index(drop=True)

        groupe_historical_data = temp.sort_values(by="Date")

        absolute_baseline_mae = mean_absolute_error(groupe_data["groupe Baseline"], groupe_data["Historique"])
        absolute_ml_mae = mean_absolute_error(groupe_data["groupe ML"], groupe_data["Historique"])
        absolute_baseline_rmse = np.sqrt(mean_squared_error(groupe_data["groupe Baseline"], groupe_data["Historique"]))
        absolute_ml_rmse = np.sqrt(mean_squared_error(groupe_data["groupe ML"], groupe_data["Historique"]))
        absolute_baseline_bias = np.abs(np.mean(groupe_data["groupe Baseline"] - groupe_data["Historique"]))
        absolute_ml_bias = np.abs(np.mean(groupe_data["groupe ML"] - groupe_data["Historique"]))

        relative_baseline_mae = mean_absolute_error(
            groupe_data["groupe Baseline"], groupe_data["Historique"]
        ) / np.mean(groupe_historical_data["Historique"])
        relative_ml_mae = mean_absolute_error(groupe_data["groupe ML"], groupe_data["Historique"]) / np.mean(
            groupe_historical_data["Historique"]
        )
        relative_baseline_rmse = np.sqrt(
            mean_squared_error(groupe_data["groupe Baseline"], groupe_data["Historique"])
        ) / np.mean(groupe_historical_data["Historique"])
        relative_ml_rmse = np.sqrt(mean_squared_error(groupe_data["groupe ML"], groupe_data["Historique"])) / np.mean(
            groupe_historical_data["Historique"]
        )
        relative_baseline_bias = np.abs(
            np.mean(groupe_data["groupe Baseline"] - groupe_data["Historique"])
            / np.mean(groupe_historical_data["Historique"])
        )
        relative_ml_bias = np.abs(
            np.mean(groupe_data["groupe ML"] - groupe_data["Historique"])
            / np.mean(groupe_historical_data["Historique"])
        )

        new_line = pd.DataFrame(
            {
                "groupe": ["Total"],
                "Absolute Baseline MAE": [absolute_baseline_mae],
                "Absolute ML MAE": [absolute_ml_mae],
                "Absolute Baseline RMSE": [absolute_baseline_rmse],
                "Absolute ML RMSE": [absolute_ml_rmse],
                "Absolute Baseline Bias": [absolute_baseline_bias],
                "Absolute ML Bias": [absolute_ml_bias],
                "Relative Baseline MAE": [relative_baseline_mae],
                "Relative ML MAE": [relative_ml_mae],
                "Relative Baseline RMSE": [relative_baseline_rmse],
                "Relative ML RMSE": [relative_ml_rmse],
                "Relative Baseline Bias": [relative_baseline_bias],
                "Relative ML Bias": [relative_ml_bias],
            }
        )

        metrics = pd.concat([metrics, new_line], axis=0, ignore_index=True)

        print(metrics)
    else:
        metrics = None
        new_horizon = 0

    return metrics, new_horizon


def create_cash_position(full_dataset):
    # init et ajoute les points
    sm_cash_position_today = 0
    sm_cash_position_today_temp = 0
    sm_cash_position_amount = 0
    sm_position_date = dt.datetime.now().date()

    sm_list_cash_position = pd.DataFrame({"Date": [sm_position_date], "Value": [0]})

    sm_predictions_position_cash = full_dataset.copy()

    for col in signed_column:
        sm_predictions_position_cash[col] = sm_predictions_position_cash[col] * (
            1 - 2 * sm_predictions_position_cash["groupe"].str.startswith("Dec")
        )

    sm_predictions_position_cash = sm_predictions_position_cash.drop(["groupe"], axis=1).groupby(by="Date").sum()
    sm_predictions_position_cash.insert(0, "Date", sm_predictions_position_cash.index)
    sm_predictions_position_cash = sm_predictions_position_cash.reset_index(drop=True)

    sm_predictions_position_cash["groupe ML"] = np.cumsum(sm_predictions_position_cash["groupe ML"])
    sm_predictions_position_cash["groupe Baseline"] = np.cumsum(sm_predictions_position_cash["groupe Baseline"])

    sm_predictions_position_cash_displayed_no_nan = full_dataset[full_dataset["Historique"].notnull()]

    if len(sm_predictions_position_cash_displayed_no_nan) > 0:
        new_horizon = (
            sm_predictions_position_cash_displayed_no_nan["Date"].max()
            - sm_predictions_position_cash_displayed_no_nan["Date"].min()
        ).days + 1
    else:
        new_horizon = 0

    sm_predictions_position_cash["Historique"] = list(
        np.cumsum(sm_predictions_position_cash["Historique"][:new_horizon])
    ) + [np.nan] * (len(sm_predictions_position_cash) - new_horizon)

    sm_predictions_position_cash_displayed = sm_predictions_position_cash.copy()

    cash_position_dict = {
        "sm_predictions_position_cash": sm_predictions_position_cash,
        "sm_predictions_position_cash_displayed": sm_predictions_position_cash_displayed,
        "sm_cash_position_today": sm_cash_position_today,
        "sm_cash_position_today_temp": sm_cash_position_today_temp,
        "sm_cash_position_amount": sm_cash_position_amount,
        "sm_position_date": sm_position_date,
        "sm_list_cash_position": sm_list_cash_position,
    }

    return cash_position_dict


#################################################################
raw_historical_data_cfg = Config.configure_data_node(
    id="raw_historical_data", path="raw_historical_data.csv", has_header=True, storage_type="csv", scope=Scope.GLOBAL
)

historical_data_cfg = Config.configure_data_node(id="historical_data", scope=Scope.GLOBAL)

task_historical_cfg = Config.configure_task(
    id="task_historical_data", function=convert_raw_history, input=[raw_historical_data_cfg], output=historical_data_cfg
)

tasks = []
predictions_list = []

for group in groups:
    # Predictions
    parameters_cfg = Config.configure_data_node(id="parameters_" + group.lower(), scope=Scope.PIPELINE)

    raw_predictions_cfg = Config.configure_data_node(
        id="raw_predictions_" + group.lower(),
        scope=Scope.PIPELINE,
        validity_period=dt.timedelta(days=7),
        cacheable=True,
    )

    task_predict_cfg = Config.configure_task(
        id="predict_" + group.lower(), function=predict, input=parameters_cfg, output=raw_predictions_cfg
    )

    tasks += [task_predict_cfg]

    metadata_cfg = Config.configure_data_node(id="metadata_" + group.lower(), scope=Scope.PIPELINE)

    predictions_cfg = Config.configure_data_node(id="predictions_" + group.lower())

    predictions_list.append(predictions_cfg)

    task_convert_cfg = Config.configure_task(
        id="convert_" + group.lower(),
        function=convert_predictions,
        input=[raw_predictions_cfg, parameters_cfg],
        output=[predictions_cfg, metadata_cfg],
    )

    tasks += [task_convert_cfg]

pipeline_predictions_cfg = Config.configure_pipeline(id="pipeline_predictions", task_configs=tasks)

# Aggregations of Predictions
full_dataset_predictions_cfg = Config.configure_data_node(id="full_dataset_predictions")

task_aggregate_cfg = Config.configure_task(
    id="task_aggregate_predictions",
    function=aggregate_predictions,
    input=predictions_list,
    output=[full_dataset_predictions_cfg],
)

pipeline_aggregate_predictions_cfg = Config.configure_pipeline(
    id="pipeline_aggregate_predictions", task_configs=[task_aggregate_cfg]
)

full_dataset_cfg = Config.configure_data_node(id="full_dataset")

task_aggregate_historical_cfg = Config.configure_task(
    id="task_aggregate_historical_data",
    function=aggregate_historic,
    input=[full_dataset_predictions_cfg, historical_data_cfg],
    output=full_dataset_cfg,
)

final_dataset_cfg = Config.configure_data_node(id="final_dataset")
reformist_cfg = Config.configure_data_node(
    id="reformist", default_data=pd.DataFrame({"Date": [], "groupe": [], "value Baseline": [], "value ML": []})
)

task_reform_cfg = Config.configure_task(
    id="task_reform", function=reform_dataset, input=[full_dataset_cfg, reformist_cfg], output=[final_dataset_cfg]
)

pipeline_historical_data_cfg = Config.configure_pipeline(
    id="pipeline_historical_data", task_configs=[task_historical_cfg]
)

metrics_cfg = Config.configure_data_node(id="metrics")
wanted_horizon_cfg = Config.configure_data_node(id="wanted_horizon", default_data=84)
real_horizon_cfg = Config.configure_data_node(id="real_horizon", default_data=84)

task_metrics_cfg = Config.configure_task(
    id="task_create_metrics",
    function=create_metrics,
    input=[final_dataset_cfg, wanted_horizon_cfg, historical_data_cfg],
    output=[metrics_cfg, real_horizon_cfg],
)

cash_position_dict_cfg = Config.configure_data_node(id="cash_position_dict")

task_cash_position_cfg = Config.configure_task(
    id="task_cash_position", function=create_cash_position, input=[final_dataset_cfg], output=[cash_position_dict_cfg]
)

pipeline_result_cfg = Config.configure_pipeline(
    id="pipeline_result",
    task_configs=[task_aggregate_historical_cfg, task_reform_cfg, task_metrics_cfg, task_cash_position_cfg],
)

# Configuration of scenario
scenario_cfg = Config.configure_scenario(
    id="scenario",
    pipeline_configs=[pipeline_historical_data_cfg, pipeline_predictions_cfg]
    + [pipeline_aggregate_predictions_cfg, pipeline_result_cfg],
    frequency=Frequency.WEEKLY,
)
