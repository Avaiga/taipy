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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import datetime

from taipy.gui import Gui

# Retrieved history:
# (Open, Close, Low, High)
stock_history = [
    (311.05, 311.00, 310.75, 311.33),
    (308.53, 308.31, 307.72, 309.00),
    (307.35, 306.24, 306.12, 307.46),
    (306.35, 304.90, 304.34, 310.10),
    (304.90, 302.99, 302.27, 307.00),
    (303.03, 301.66, 301.20, 303.25),
    (301.61, 299.58, 299.50, 301.89),
    (299.58, 297.95, 297.80, 300.06),
    (297.95, 299.03, 297.14, 299.67),
    (299.03, 301.87, 296.71, 301.89),
    (301.89, 299.40, 298.73, 302.93),
    (299.50, 299.35, 298.83, 299.50),
    (299.35, 299.20, 299.19, 299.68),
    (299.42, 300.50, 299.42, 300.50),
    (300.70, 300.65, 300.32, 300.75),
    (300.65, 299.91, 299.91, 300.76),
]
start_date = datetime.datetime(year=2022, month=10, day=21)
period = datetime.timedelta(seconds=4 * 60 * 60)  # 4 hours

data = {
    # Compute date series
    "Date": [start_date + n * period for n in range(0, len(stock_history))],
    # Extract open values
    "Open": [v[0] for v in stock_history],
    # Extract close values
    "Close": [v[1] for v in stock_history],
    # Extract low values
    "Low": [v[2] for v in stock_history],
    # Extract high values
    "High": [v[3] for v in stock_history],
}

md = """
# Candlestick - Timeline

<|{data}|chart|type=candlestick|x=Date|open=Open|close=Close|low=Low|high=High|>
"""

Gui(md).run()
