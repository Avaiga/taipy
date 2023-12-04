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
import io
from decimal import Decimal, getcontext

from taipy.gui import Gui, download

# Initial precision
precision = 10


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


# Generate the digits, save them in a CSV file content, and trigger a download action
# so the user can retrieve them
def download_pi(state):
    digits = pi(state.precision)
    buffer = io.StringIO()
    buffer.write("index,digit\n")
    for i, d in enumerate(digits):
        buffer.write(f"{i},{d}\n")
    download(state, content=bytes(buffer.getvalue(), "UTF-8"), name="pi.csv")


page = """
# File Download - Dynamic content

Precision:

<|{precision}|slider|min=2|max=10000|>

<|{None}|file_download|on_action=download_pi|label=Download Pi digits|>
"""

Gui(page).run()
