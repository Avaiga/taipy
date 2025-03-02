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
# Stock page.
# -----------------------------------------------------------------------------------------
from taipy.gui import Markdown

# Whether stock details are displayed or not
show_details = False

# Compute and return the total stock value based on purchase price and stock quantity
def compute_stock_value(data: dict[str, list[float]]) -> float:
    return sum([v * n for v, n in zip(data["Purchase"], data["Stock"])])

# Define the Stock page as a Markdown page
page = Markdown("""# Stock

Stock value: $<|{compute_stock_value(data)}|>

<|Stock details|expandable|expanded={show_details}|
<|{data}|table|columns=Items;Stock|>
|>

[Goto Sales](sales)
""")
