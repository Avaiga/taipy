from operator import attrgetter

import markdown
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

from ..app import App
from ..utils import getDataType


# The field pattern also handles the [<var>] construct
class FieldPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): field+attributes
    # group(4): attributes
    _PATTERN = r"\[(?:TaIpY([a-zA-Z][\.a-zA-Z_$0-9]*)\{(\d+)\})?(field\s*(?:\:\s*(.*?))?)?\s*\]"

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-field"] = FieldPattern(FieldPattern._PATTERN, md)

    # TODO: Attributes:
    #   on_update=<func>
    def handleMatch(self, m, data):
        """Handle the match."""

        value = "<empty>"
        var_name = m.group(1)
        var_id = m.group(2)
        if var_name:
            try:
                # Bind variable name (var_name string split in case var_name is a dictionary)
                App._get_instance().bind_var(var_name.split(sep=".")[0])
                value = attrgetter(var_name)(App._get_instance()._values)
            except:
                print("error")
                value = "[Undefined: " + var_name + "]"

        if m.group(3):
            el = etree.Element("Input")
            el.set(
                "class",
                "taipy-field " + App._get_instance()._config.style_config["input"],
            )
            if var_name:
                # TODO: or oninput (continuous updates)
                el.set("onchange", "onUpdate(this.id, this.value)")
            el.set("type", "text")
            el.set("value", str(value))
        else:
            el = etree.Element("Field")
            el.set(
                "className",
                "taipy-var " + App._get_instance()._config.style_config["field"],
            )
            el.set("value", str(value))
            el.set("dataType", getDataType(value))
        if var_name:
            el.set("key", var_name + "_" + str(var_id))
            el.set(
                "tp_" + var_name.replace(".", "__"),
                "{!" + var_name.replace(".", "__") + "!}",
            )
            el.set("tp_varname", var_name)

        return el, m.start(0), m.end(0)
