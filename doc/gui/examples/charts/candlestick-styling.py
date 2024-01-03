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
# You may need to install the yfinance package as well.
# -----------------------------------------------------------------------------------------
import yfinance
from taipy.gui import Gui

# Extraction of a few days of stock historical data for AAPL using
# the yfinance package (see https://pypi.org/project/yfinance/).
# The returned value is a Pandas DataFrame.
ticker = yfinance.Ticker("AAPL")
stock = ticker.history(interval="1d", start="2018-08-18", end="2018-09-10")
# Copy the DataFrame index to a new column
stock["Date"] = stock.index

options = {
    # Candlesticks that show decreasing values are orange
    "decreasing": {"line": {"color": "orange"}},
    # Candlesticks that show decreasing values are blue
    "increasing": {"line": {"color": "blue"}},
}

layout = {
    "xaxis": {
        # Hide the range slider
        "rangeslider": {"visible": False}
    }
}

page = """
# Candlestick - Styling

<|{stock}|chart|type=candlestick|x=Date|open=Open|close=Close|low=Low|high=High|options={options}|layout={layout}|>
"""

Gui(page).run()
