from datetime import datetime

from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder


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

    def handleMatch(self, m, data):
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="DateSelector",
                has_attribute=True,
                default_value="",
            )
            .get_app_value(fallback_value=datetime.fromtimestamp(0))
            .set_varname()
            .set_default_value()
            .set_className(
                class_name="taipy-date-selector", config_class="date_selector"
            )
            .set_withTime()
            .build()
        )
