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

if __name__ == "__main__":
    # Tasks definitions
    tasks = ["Plan", "Research", "Design", "Implement", "Test", "Deliver"]
    # Task durations, in days
    durations = [50, 30, 30, 40, 15, 10]
    # Planned start dates of tasks
    start_dates = [
        datetime.date(2022, 10, 15),  # Plan
        datetime.date(2022, 11, 7),  # Research
        datetime.date(2022, 12, 1),  # Design
        datetime.date(2022, 12, 20),  # Implement
        datetime.date(2023, 1, 15),  # Test
        datetime.date(2023, 2, 1),  # Deliver
    ]

    epoch = datetime.date(1970, 1, 1)

    data = {
        "start": start_dates,
        "Task": tasks,
        # Compute the time span as adatetime (relative to January 1st, 1970)
        "Date": [epoch + datetime.timedelta(days=duration) for duration in durations],
    }

    layout = {
        "yaxis": {
            # Sort tasks from top to bottom
            "autorange": "reversed",
            # Remove title
            "title": {"text": ""},
        },
    }

    page = """
# Gantt - Simple

<|{data}|chart|type=bar|orientation=h|y=Task|x=Date|base=start|layout={layout}|>
    """

    Gui(page).run()
