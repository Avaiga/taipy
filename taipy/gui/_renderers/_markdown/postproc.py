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

from markdown.treeprocessors import Treeprocessor

from ..builder import _Builder


class _Postprocessor(Treeprocessor):
    @staticmethod
    def extend(md, gui, priority):
        instance = _Postprocessor(md)
        md.treeprocessors.register(instance, "taipy", priority)
        instance._gui = gui

    def run(self, root):
        MD_PARA_CLASSNAME = "md-para"
        for p in root.iter():
            if p.tag == "p":
                classes = p.get("class")
                classes = f"{MD_PARA_CLASSNAME} {classes}" if classes else MD_PARA_CLASSNAME
                p.set("class", classes)
                p.tag = "div"
            if p != root:
                p.set("key", _Builder._get_key(p.tag))
        return root
