from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder


class ButtonPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): attributes
    _PATTERN = (
        r"\[(?:TaIpY([a-zA-Z][a-zA-Z_$0-9]*)\{(\d+)\})?button\s*(?:\:\s*(.*?))?\s*\]"
    )

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-button"] = ButtonPattern(ButtonPattern._PATTERN, md)

    def handleMatch(self, m, data):
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Input",
                has_attribute=True,
                default_value="<empty>",
            )
            .set_type("button")
            .get_app_value()
            .set_varname()
            .set_default_value()
            .set_className(class_name="taipy-button", config_class="button")
            .set_button_attribute()
            .build()
        )
