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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui
from datetime import date, timedelta

# Create the list of dates (all year 2000)
all_dates = {}
all_dates_str = []
start_date = date(2000, 1, 1)
end_date = date(2001, 1, 1)
a_date = start_date
while a_date < end_date:
    date_str = a_date.strftime("%Y/%m/%d")
    all_dates_str.append(date_str)
    all_dates[date_str] = a_date
    a_date += timedelta(days=1)

# Initial selection: first and last day
dates=[all_dates_str[1], all_dates_str[-1]]
# These two variables are used in text controls
start_sel = all_dates[dates[0]]
end_sel = all_dates[dates[1]]

def on_change(state, _, var_value):
    # Update the text controls
    state.start_sel = all_dates[var_value[0]]
    state.end_sel = all_dates[var_value[1]]

page = """
# Slider - Date range

<|{dates}|slider|lov={all_dates_str}|>

Start: <|{start_sel}|text|format=d MMM|>

End: <|{end_sel}|text|format=d MMM|>
"""

Gui(page).run()
