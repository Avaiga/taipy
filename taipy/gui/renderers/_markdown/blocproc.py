import re

from markdown.blockprocessors import BlockProcessor

from .factory import MarkdownFactory


class StartBlockProcessor(BlockProcessor):
    __RE_FENCE_START = re.compile(
        MarkdownFactory._TAIPY_START + r"([a-zA-Z][\.a-zA-Z_$0-9]*)\.start(.*?)" + MarkdownFactory._TAIPY_END
    )  # start line
    __RE_OTHER_FENCE = re.compile(
        MarkdownFactory._TAIPY_START + r"([a-zA-Z][\.a-zA-Z_$0-9]*)\.(start|end)(.*?)" + MarkdownFactory._TAIPY_END
    )  # start or end tag

    def test(self, parent, block):
        return re.match(StartBlockProcessor.__RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        original_match = re.search(StartBlockProcessor.__RE_FENCE_START, original_block)
        blocks[0] = re.sub(StartBlockProcessor.__RE_FENCE_START, "", blocks[0], 1)
        tag = original_match.group(1)
        queue = [tag]
        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            matches = re.findall(StartBlockProcessor.__RE_OTHER_FENCE, block)
            for match in matches:
                if queue[-1] == match[0] and match[1] == "end":
                    queue.pop()
                elif match[1] == "start":
                    queue.append(match[0])
            if len(queue) == 0:
                # remove end fence
                blocks[block_num] = re.sub(
                    MarkdownFactory._TAIPY_START + tag + r"\.end(.*?)" + MarkdownFactory._TAIPY_END,
                    "",
                    block,
                    1,
                )
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
