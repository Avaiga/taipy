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

import re

from markdown.blockprocessors import BlockProcessor

from .factory import _MarkdownFactory


class _StartBlockProcessor(BlockProcessor):
    __RE_FENCE_START = re.compile(
        _MarkdownFactory._TAIPY_START + r"([a-zA-Z][\.a-zA-Z_$0-9]*)\.start(.*?)" + _MarkdownFactory._TAIPY_END
    )  # start line
    __RE_OTHER_FENCE = re.compile(
        _MarkdownFactory._TAIPY_START + r"([a-zA-Z][\.a-zA-Z_$0-9]*)\.(start|end)(.*?)" + _MarkdownFactory._TAIPY_END
    )  # start or end tag

    @staticmethod
    def extend(md, gui, priority):
        instance = _StartBlockProcessor(md.parser)
        md.parser.blockprocessors.register(instance, "taipy", priority)
        instance._gui = gui

    def test(self, parent, block):
        return re.match(_StartBlockProcessor.__RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        original_match = re.search(_StartBlockProcessor.__RE_FENCE_START, original_block)
        blocks[0] = re.sub(_StartBlockProcessor.__RE_FENCE_START, "", blocks[0], count=1)
        tag = original_match.group(1)
        stack = [tag]
        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            matches = re.findall(_StartBlockProcessor.__RE_OTHER_FENCE, block)
            for match in matches:
                if stack[-1] == match[0] and match[1] == "end":
                    stack.pop()
                elif match[1] == "start":
                    stack.append(match[0])
            if not stack:
                # remove end fence
                blocks[block_num] = re.sub(
                    _MarkdownFactory._TAIPY_START + tag + r"\.end(.*?)" + _MarkdownFactory._TAIPY_END,
                    "",
                    block,
                    count=1,
                )
                # render fenced area inside a new div
                e = _MarkdownFactory.create_element(self._gui, original_match.group(1), original_match.group(2))
                parent.append(e)
                # parse inside blocks
                self.parser.parseBlocks(e, blocks[: block_num + 1])
                # remove used blocks
                del blocks[: block_num + 1]
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False
