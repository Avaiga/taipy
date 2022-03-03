from markdown.inlinepatterns import InlineProcessor

from .factory import _MarkdownFactory


class _ControlPattern(InlineProcessor):

    __PATTERN = _MarkdownFactory._TAIPY_START + "([a-zA-Z][\\.a-zA-Z_$0-9]*)(.*?)" + _MarkdownFactory._TAIPY_END

    @staticmethod
    def extend(md, gui, priority):
        instance = _ControlPattern(_ControlPattern.__PATTERN, md)
        md.inlinePatterns.register(instance, "taipy", priority)
        instance._gui = gui

    def handleMatch(self, m, data):
        return _MarkdownFactory.create_element(self._gui, m.group(1), m.group(2)), m.start(0), m.end(0)
