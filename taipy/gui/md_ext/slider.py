from markdown.inlinepatterns import InlineProcessor
from .builder import MarkdownBuilder


class SliderPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): attributes
    _PATTERN = (
        r"\[(?:TaIpY([a-zA-Z][a-zA-Z_$0-9]*)\{(\d+)\})?slider\s*(?:\:\s*(.*?))?\s*\]"
    )

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-slider"] = SliderPattern(SliderPattern._PATTERN, md)

    def handleMatch(self, m, data):
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Input",
                has_attribute=False,
                default_value=0,
            )
            .set_type("range")
            .get_app_value(fallback_value=0)
            .set_varname()
            .set_value()
            .set_className(class_name="taipy-slider", config_class="slider")
            .set_attribute("min", "1")
            .set_attribute("max", "100")
            .build()
        )
