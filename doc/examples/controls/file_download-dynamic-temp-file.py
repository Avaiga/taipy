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
from taipy.gui import Gui, download
from decimal import getcontext, Decimal
from tempfile import NamedTemporaryFile
import os

# Initial precision
precision = 10
# Stores the path to the temporary file
temp_path = None


def pi(precision: int) -> list[int]:
    """Compute Pi to the required precision.

    Adapted from https://docs.python.org/3/library/decimal.html
    """
    saved_precision = getcontext().prec  # Save precision
    getcontext().prec = precision
    three = Decimal(3)  # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    digits = []
    while s != 0:
        integral = int(s)
        digits.append(integral)
        s = (s - integral) * 10
    getcontext().prec = saved_precision
    return digits


# Remove the temporary file
def clean_up(state):
    os.remove(state.temp_path)


# Generate the digits, save them in a CSV temporary file, then trigger a download action
# for that file.
def download_pi(state):
    digits = pi(state.precision)
    with NamedTemporaryFile("r+t", suffix=".csv", delete=False) as temp_file:
        state.temp_path = temp_file.name
        temp_file.write("index,digit\n")
        for i, d in enumerate(digits):
            temp_file.write(f"{i},{d}\n")
    download(state, content=temp_file.name, name="pi.csv", on_action=clean_up)


page = """
# File Download - Dynamic content

Precision:

<|{precision}|slider|min=2|max=10000|>

<|{None}|file_download|on_action=download_pi|label=Download Pi digits|>
"""

Gui(page).run()
