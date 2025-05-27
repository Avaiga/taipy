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
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import io

from PIL import Image

from taipy.gui import Gui, State

path = ""
image = None

def upload(state: State):
    img = Image.open(state.path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    state.image = img_byte_arr.getvalue()

page = """
<|{path}|file_selector|on_action=upload|extensions=png,jpg|>
<|{image}|image|>
"""

if __name__ == "__main__":
    Gui(page).run(title="File Selector - With image")
