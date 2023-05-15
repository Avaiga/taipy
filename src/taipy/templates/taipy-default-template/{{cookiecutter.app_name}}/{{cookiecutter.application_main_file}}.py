# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime
import webbrowser

import pandas as pd

import taipy as tp
from taipy.gui import notify

DOWNLOAD_PATH = "data/weather.csv"
upload_file = None

page = """
<center>
<|navbar|lov={[("page1", "Dashboard"), ("https://docs.taipy.io/en/latest/manuals/about/", "Taipy Docs"), ("https://docs.taipy.io/en/latest/getting_started/", "Getting Started")]}|>
</center>

Taipy Data Dashboard template
=============================
<|layout|columns=1 3|
<|
### Let's create a simple Data Dashboard!
<br/>
<center>
    <|{upload_file}|file_selector|label=Upload Dataset|>
</center>
|>
<|
<center>
    <|{logo}|image|height=250px|width=250px|on_action=image_action|>
</center>
|>
|>

## Data Visualization
<|{dataset}|chart|mode=lines|x=Date|y[1]=MinTemp|y[2]=MaxTemp|color[1]=blue|color[2]=red|>

<|layout|columns= 1 5|
<|

## Custom Parameters
**Starting Date**\n\n<|{start_date}|date|not with_time|on_change=start_date_onchange|>
<br/><br/>
**Ending Date**\n\n<|{end_date}|date|not with_time|on_change=end_date_onchange|>
<br/>
<br/>
<|button|label=GO|on_action=button_action|>
|>
<|
<center>
    <h2>Dataset</h2><|{DOWNLOAD_PATH}|file_download|on_action=download|>
    <|{dataset}|table|page_size=10|height=500px|width=65%|>
</center>
|>
|>
"""


def image_action(state):
    webbrowser.open("https://taipy.io")


def get_data(path: str):
    dataset = pd.read_csv(path)
    dataset["Date"] = pd.to_datetime(dataset["Date"]).dt.date
    return dataset


def start_date_onchange(state, var_name, value):
    state.start_date = value.date()


def end_date_onchange(state, var_name, value):
    state.end_date = value.date()


def filter_by_date_range(dataset, start_date, end_date):
    mask = (dataset["Date"] > start_date) & (dataset["Date"] <= end_date)
    return dataset.loc[mask]


def button_action(state):
    state.dataset = filter_by_date_range(dataset, state.start_date, state.end_date)
    notify(
        state,
        "info",
        "Updated date range from {} to {}.".format(
            state.start_date.strftime("%m/%d/%Y"), state.end_date.strftime("%m/%d/%Y")
        ),
    )


def download(state):
    state.dataset.to_csv(DOWNLOAD_PATH)


logo = "images/taipy_logo.jpg"
dataset = get_data("data/weather.csv")
start_date = datetime.date(2008, 12, 1)
end_date = datetime.date(2017, 6, 25)


if __name__ == "__main__":
    tp.Gui(page=page).run(
        title="{{cookiecutter.application_title}}",
        dark_mode=False,
    )
