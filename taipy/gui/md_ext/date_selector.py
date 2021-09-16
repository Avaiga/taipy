from datetime import datetime
from operator import attrgetter

import markdown
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

from ..app import App
from ..utils import dateToISO, is_boolean_true
from .parse_attributes import parse_attributes


class DateSelectorPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): attributes
    _PATTERN = r"\[(?:TaIpY([a-zA-Z][\.a-zA-Z_$0-9]*))\{(\d+)\}date_selector\s*(?:\:\s*(.*?))?\s*\]"

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-date-selector"] = DateSelectorPattern(
            DateSelectorPattern._PATTERN, md
        )

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
            value = datetime.fromtimestamp(0)

        el = etree.Element("DateSelector")
        el.set(
            "className",
            "taipy-date-selector "
            + App._get_instance()._config.style_config["date_selector"],
        )
        if var_name:
            el.set("key", var_name + "_" + str(var_id))
            el.set(
                "tp_" + var_name.replace(".", "__"),
                "{!" + var_name.replace(".", "__") + "!}",
            )
            el.set("tp_varname", var_name)
        el.set("value", dateToISO(value))

        attributes = parse_attributes(m.group(3))
        if (
            attributes
            and "with_time" in attributes
            and is_boolean_true(attributes["with_time"])
        ):
            el.set("withTime", str(True))

        return el, m.start(0), m.end(0)
