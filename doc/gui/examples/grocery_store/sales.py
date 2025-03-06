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
# Example on Page Modules.
# Sales page.
# -----------------------------------------------------------------------------------------
from taipy.gui import Markdown, Page


# SalesPage inherits from taipy.gui.Page
class SalesPage(Page):
    def __init__(self) -> None:
        self.quarter = "Q1"  # Initial selected quarter
        self.currency = "$"  # Initial currency
        super().__init__()

    @staticmethod
    def compute_total(quarter: str, currency: str, data: dict[str, list[float]]) -> float:
        """Compute the total sales revenue for the selected quarter and currency."""
        # Sales data for the chosen quarter
        sold = data[f"Sales {quarter}"]
        # Prices in the chosen currency
        price = data[f"Price {currency}"]
        # Compute and return total revenue
        return sum(s * p for s, p in zip(sold, price))

    def create_page(self):
        """Create and return the page content."""
        return Markdown("""
# Sales

<|1 4|layout
Select quarter: <|{quarter}|selector|lov=Q1;Q2;Q3|>

Total: <|{SalesPage.compute_total(quarter, currency, data)}|format=%.02f|><br/>
Currency: <|{currency}|toggle|lov=$;€|>
|>

<|{data}|table|columns=Items;Sales Q1;Sales Q2;Sales Q3|>

[Goto Stock](stock)
""")
