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
import os
import re
import typing as t
from unittest.mock import patch

from taipy.gui import Gui
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType


class TgbLibrary(ElementLibrary):
    elements = {
        "e1": Element(
            "s1",
            {
                "b1": ElementProperty(PropertyType.boolean),
                "b2": ElementProperty(PropertyType.dynamic_boolean, doc_string=""),
                "s1": ElementProperty(PropertyType.string, doc_string="e1.s1 doc"),
                "s2": ElementProperty(
                    PropertyType.dynamic_string,
                    doc_string="""e1.s2 doc
                                      More e1.s2 doc""",
                ),
                "d1": ElementProperty(
                    PropertyType.dict,
                    doc_string="""
                    e1.d1 doc
                    More e1.d1 doc""",
                ),
                "d2": ElementProperty(
                    PropertyType.dynamic_dict,
                    doc_string="""
                    e1.d2 doc

                    More e1.d2 doc""",
                ),
            },
            "E1",
            doc_string="e1 doc",
        ),
        "e2": Element(
            "x",
            {
                "p1": ElementProperty(PropertyType.boolean),
                "p2": ElementProperty(PropertyType.boolean),
                "p3": ElementProperty(PropertyType.boolean, type_hint="Union[bool,str]"),
            },
            "E2",
        ),
    }

    def get_name(self) -> str:
        return "test_ext_tgb"

    def get_elements(self) -> t.Dict[str, Element]:
        return TgbLibrary.elements


def test_tgb_generation(gui: Gui, test_client, helpers):
    from taipy.gui.extension._main._generate_tgb import generate_doc

    library = TgbLibrary()
    api = generate_doc(library)
    assert "def e1(" in api, "Missing element e1"
    assert "s1" in api, "Missing property s1"
    assert re.search(r"\(\s*s1\s*:", api), "Property s1 should be the default property"
    assert re.search(r"b1:\s*t.Optional\[t.Union\[bool", api), "Incorrect property type for b1"
    assert re.search(r"b2:\s*t.Optional\[t.Union\[bool", api), "Incorrect property type for b2"
    assert re.search(r"s1:\s*t.Optional\[str\]", api), "Incorrect property type for s1"
    assert re.search(r"s2:\s*t.Optional\[str\]", api), "Incorrect property type for s2"
    assert re.search(r"d1:\s*t.Optional\[t.Union\[dict", api), "Incorrect property type for d1"
    assert re.search(r"d2:\s*t.Optional\[t.Union\[dict", api), "Incorrect property type for d2"
    assert "e1 doc" in api, "Missing doc for e1"
    assert "`b1`: ..." in api, "Doc for e1.b1 should be empty"
    assert "`b2`: ..." in api, "Doc for e1.b1 should be empty"
    assert "`s1`: e1.s1 doc" in api, "Doc for e1.s1 is wrong"
    assert "`s2`: e1.s2 doc\n        More e1.s2 doc" in api, "Doc for e1.s2 is wrong"
    assert "`d1`: e1.d1 doc\n        More e1.d1 doc" in api, "Doc for e1.d1 is wrong"
    assert "`d2`: e1.d2 doc\n\n        More e1.d2 doc" in api, "Doc for e1.d2 is wrong"
    assert "def e2(" in api, "Missing element e2"
    assert re.search(r"\(\s*p1\s*:", api), "Wrong default property in e2"
    assert re.search(r"p3:\s*t\.Union", api), "Wrong type hint for property p3 in e2"


def test_tgb_generation_entry_point(gui: Gui, test_client, helpers):
    import tempfile

    from taipy.gui.extension.__main__ import main

    saved_cwd = os.getcwd()
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    os.chdir(os.path.dirname(__file__))
    try:
        with patch("sys.argv", ["main", "generate_tgb", "extlib_test", temp_file.name]):
            assert main() == 0
    finally:
        os.chdir(saved_cwd)
        os.remove(temp_file.name)
