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

import taipy.gui.builder as tgb
from taipy.gui import Gui
from taipy.gui.data.decimator import ScatterDecimator


def test_decimator_embed_object(gui: Gui, test_client, helpers):
    chart_builder = tgb.chart(decimator=ScatterDecimator())  # type: ignore[attr-defined] # noqa: B023
    frame_locals = locals()
    decimator_property = chart_builder._properties.get("decimator", None)
    assert decimator_property is not None
    assert decimator_property in frame_locals
    assert isinstance(frame_locals[decimator_property], ScatterDecimator)
