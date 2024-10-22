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

from taipy import Gui

# Extraction of a month of stock data for AAPL using the
# yfinance package (see https://pypi.org/project/yfinance/).
ticker = yfinance.Ticker("AAPL")
# The returned value is a Pandas DataFrame.
stock = ticker.history(interval="1d", start="2018-08-01", end="2018-08-31")
# Copy the DataFrame's index to a new column
stock["Date"] = stock.index

page = """
<|{stock}|chart|type=candlestick|x=Date|open=Open|close=Close|low=Low|high=High|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Candlestick - Simple")
