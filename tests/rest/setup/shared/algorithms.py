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

import pickle
import random
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd

n_predictions = 14


def forecast(model, date: datetime):
    dates = [date + timedelta(days=i) for i in range(n_predictions)]
    forecasts = [f + random.uniform(0, 2) for f in model.forecast(len(dates))]
    days = [str(dt.date()) for dt in dates]
    res = {"Date": days, "Forecast": forecasts}
    return pd.DataFrame.from_dict(res)


def evaluate(cleaned: pd.DataFrame, forecasts: pd.DataFrame, date: datetime) -> Dict[str, Any]:
    cleaned = cleaned[cleaned["Date"].isin(forecasts["Date"].tolist())]
    forecasts_as_series = pd.Series(forecasts["Forecast"].tolist(), name="Forecast")
    res = pd.concat([cleaned.reset_index(), forecasts_as_series], axis=1)
    res["Delta"] = abs(res["Forecast"] - res["Value"])

    return {
        "Date": date,
        "Dataframe": res,
        "Mean_absolute_error": res["Delta"].mean(),
        "Relative_error": (res["Delta"].mean() * 100) / res["Value"].mean(),
    }


if __name__ == "__main__":
    model = pickle.load(open("../my_model.p", "rb"))
    day = datetime(2020, 1, 25)
    forecasts = forecast(model, day)

    historical_temperature = pd.read_csv("../historical_temperature.csv")
    evaluation = evaluate(historical_temperature, forecasts, day)

    print(evaluation["Dataframe"])  # noqa: T201
    print()  # noqa: T201
    print(f'Mean absolute error : {evaluation["Mean_absolute_error"]}')  # noqa: T201
    print(f'Relative error in %: {evaluation["Relative_error"]}')  # noqa: T201
