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
import taipy.gui.builder as tgb
from taipy.gui import Gui

# Initially invested amount
initial_investment = 100
# Number of periods
periods = 0
# Number of periods
final_amount = initial_investment
# Interest rate by period
rate = 5
# Is the interest rate setting panel shown
show_rate = False

with tgb.Page() as rate_page:
    tgb.text("Rate (in %):")
    tgb.number("{rate}")

with tgb.Page() as page:
    tgb.text("# Interest Calculator", mode="md")

    tgb.pane("{show_rate}", show_button=True, page="_rate_pane")

    tgb.text("Initial amount: ", inline=True)
    tgb.number("{initial_investment}")

    tgb.text("Periods", inline=True)
    tgb.number("{periods}", min=0, max=50)

    tgb.text("Final amount: ", inline=True)
    tgb.text("{final_amount}", format="%.2f", inline=True)


# Invoked when any control value (initial_investment, rate, or periods) is changed.
def on_change(state, var_name: str):
    # Cumulated interest percentage
    progress = pow(1 + state.rate / 100, state.periods)
    state.final_amount = state.initial_investment * progress


pages = {
    "main": page,
    "_rate_pane": rate_page,
}

if __name__ == "__main__":
    Gui(pages=pages).run(title="Pane - As page")
