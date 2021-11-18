from markdown.blockprocessors import BlockProcessor
import re

from taipy.gui.renderers._markdown.factory import MarkdownFactory


class StartBlockProcessor(BlockProcessor):
    RE_FENCE_START = r"TaIpY:([a-zA-Z][\.a-zA-Z_$0-9]*)\.start(.*?):tAiPy"  # start line
    RE_OTHER_FENCE = (
        r"TaIpY:([a-zA-Z][\.a-zA-Z_$0-9]*)\.(start|end)(.*?):tAiPy"  # last non-blank line, e.g, '!!!\n  \n\n'
    )

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        original_match = re.search(self.RE_FENCE_START, original_block)
        blocks[0] = re.sub(self.RE_FENCE_START, "", blocks[0], 1)
        tag = original_match.group(1)
        queue = [tag]
        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            matches = re.findall(self.RE_OTHER_FENCE, block)
            for match in matches:
                if queue[-1] == match[0] and match[1] == "end":
                    queue.pop()
                elif match[1] == "start":
                    queue.append(match[0])
            if len(queue) == 0:
                # remove end fence
                blocks[block_num] = re.sub(r"TaIpY:" + tag + "\.end(.*?):tAiPy", "", block, 1)
                # render fenced area inside a new div
                e = MarkdownFactory.create_element(original_match.group(1), original_match.group(2))
                parent.append(e)
                self.parser.parseBlocks(e, blocks[0 : block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False
