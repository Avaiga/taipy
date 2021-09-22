from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder


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

    def handleMatch(self, m, data):
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Input",
                has_attribute=False,
                default_value=0,
            )
            .set_type("number")
            .get_app_value(fallback_value=0)
            .set_varname()
            .set_default_value()
            .set_className(class_name="taipy-number", config_class="input")
            .build()
        )
