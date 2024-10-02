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
from random import randrange

from taipy.gui import Gui, Markdown

x_range = range(0, 11)

# The dataset is made of three arrays:
# x: an integer value from 0 to 5
# y: the square of the value in the "x" column
# z: a random integer between 0 and 5
data = {"x": x_range, "y": [x * x for x in x_range], "z": [randrange(6) for _ in x_range]}


def xy_class(_1, _2, index, _3, column_name):
    return (
        # The background color of the 'x' column alternates between two shades of green,
        # varying in lightness.
        ("greenish" if index % 2 else "light-greenish")
        if column_name == "x"
        # The background color of the 'y' column alternates between two shades of green,
        # varying in lightness
        else ("reddish" if index % 2 else "light-reddish")
    )


def z_class(_, value):
    # Build a CSS classname from the value.
    # The lower the value is, the lighter the color is.
    return f"col{value}"


page = Markdown(
    "<|{data}|table|cell_class_name[x]=xy_class|cell_class_name[y]=xy_class|cell_class_name[z]=z_class|show_all|>",
    # Using a lambda function instead of z_class:
    # "<|{data}|table|cell_class_name[x]=xy_class|cell_class_name[y]=xy_class|cell_class_name[z]={lambda _, v: f'col{v}'}|show_all|>", # noqa: E501
    style={
        ".reddish": {"color": "white", "background-color": "#bf1313"},
        ".light-reddish": {"color": "black", "background-color": "#ff1919", "font-weight": "bold"},
        ".greenish": {"color": "white", "background-color": "#75bf75"},
        ".light-greenish": {"color": "black", "background-color": "#9cff9c", "font-weight": "bold"},
        ".col0": {"background-color": "#d0d0d0"},
        ".col1": {"background-color": "#a4a0cf"},
        ".col2": {"background-color": "#7970cf"},
        ".col3": {"background-color": "#4e40cf", "color": "white"},
        ".col4": {"background-color": "#2410cf", "color": "white"},
        ".col5": {"background-color": "#1b02a8", "color": "white"},
    },
)


if __name__ == "__main__":
    Gui(page).run(title="Table - Styling cells")
