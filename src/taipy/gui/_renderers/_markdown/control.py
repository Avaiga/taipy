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

from markdown.inlinepatterns import InlineProcessor

from .factory import _MarkdownFactory


class _ControlPattern(InlineProcessor):
    __PATTERN = _MarkdownFactory._TAIPY_START + r"([a-zA-Z][\.a-zA-Z_$0-9]*)(.*?)" + _MarkdownFactory._TAIPY_END

    @staticmethod
    def extend(md, gui, priority):
        instance = _ControlPattern(_ControlPattern.__PATTERN, md)
        md.inlinePatterns.register(instance, "taipy", priority)
        instance._gui = gui

    def handleMatch(self, m, data):
        return _MarkdownFactory.create_element(self._gui, m.group(1), m.group(2)), m.start(0), m.end(0)
