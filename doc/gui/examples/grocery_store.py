# Copyright 2021-2025 Avaiga Private Limited
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
# Entry point for the example on Page Modules.
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
from grocery_store.sales import SalesPage
from grocery_store.stock import page as StockPage

from taipy.gui import Gui

# Define sample data for grocery store sales and stock
data = {
    "Items": ["Apples", "Bananas", "Oranges", "Grapes", "Strawberries"],
    "Purchase": [1.36, 0.73, 1.09, 2.27, 2.73],
    "Price $": [1.50, 0.80, 1.20, 2.50, 3.00],
    "Price €": [1.38, 0.74, 1.10, 2.30, 2.76],
    "Sales Q1": [120, 200, 90, 50, 75],
    "Sales Q2": [140, 180, 110, 60, 85],
    "Sales Q3": [100, 190, 95, 55, 80],
    "Stock": [500, 600, 400, 300, 250],
}

# Initialize and run the GUI application with Sales and Stock pages
if __name__ == "__main__":
    Gui(pages={"sales": SalesPage(), "stock": StockPage}).run(title="Grocery Store")
