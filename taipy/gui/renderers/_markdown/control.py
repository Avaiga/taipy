import re

from markdown.inlinepatterns import InlineProcessor

from .factory import MarkdownFactory


class ControlPattern(InlineProcessor):

    __PATTERN = MarkdownFactory._TAIPY_START + "([a-zA-Z][\.a-zA-Z_$0-9]*)(.*?)" + MarkdownFactory._TAIPY_END

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns.register(ControlPattern(ControlPattern.__PATTERN, md), "taipy-control", 205)

    def handleMatch(self, m, data):
        return MarkdownFactory.create_element(m.group(1), m.group(2)), m.start(0), m.end(0)
