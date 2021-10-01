import re
from markdown.inlinepatterns import InlineProcessor

from .factory import Factory


class ControlPattern(InlineProcessor):

    _PATTERN = r"<\|taipy\.(.*?)\|(.*?)\|>"

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-control"] = ControlPattern(ControlPattern._PATTERN, md)

    def handleMatch(self, m, data):
        return Factory.create(m.group(1), m.group(2)), m.start(0), m.end(0)
