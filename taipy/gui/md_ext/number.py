from operator import attrgetter

import markdown
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

from ..app import App


class NumberPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): attributes
    _PATTERN = (
        r"\[(?:TaIpY([a-zA-Z][a-zA-Z_$0-9]*))\{(\d+)\}number\s*(?:\:\s*(.*?))?\s*\]"
    )

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-number"] = NumberPattern(NumberPattern._PATTERN, md)

    # TODO: Attributes:
    #   on_update=<func>
    def handleMatch(self, m, data):
        """Handle the match."""

        var_name = m.group(1)
        var_id = m.group(2)
        try:
            App._get_instance().bind_var(var_name.split(sep=".")[0])
            value = attrgetter(var_name)(App._get_instance()._values)
        except:
            value = "[Undefined: " + var_name + "]"

        el = etree.Element("Input")
        el.set(
            "className",
            "taipy-number " + App._get_instance()._config.style_config["input"],
        )
        if var_name:
            el.set("key", var_name + "_" + str(var_id))
            # TODO: or oninput (continuous updates)
            el.set("onchange", "onUpdate(this.id, this.value)")
            el.set(
                "tp_" + var_name.replace(".", "__"),
                "{!" + var_name.replace(".", "__") + "!}",
            )
            el.set("tp_varname", var_name)
        el.set("type", "number")
        el.set("value", str(value))

        return el, m.start(0), m.end(0)
