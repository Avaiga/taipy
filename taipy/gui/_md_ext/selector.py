from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder


# The selector pattern also handles the [<var>] construct
class SelectorPattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): selector+attributes
    # group(4): attributes
    _PATTERN = r"\[(?:TaIpY([a-zA-Z][\.a-zA-Z_$0-9]*)\{(\d+)\})?(selector\s*(?:\:\s*(.*?))?)?\s*\]"  # noqa

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-selector"] = SelectorPattern(
            SelectorPattern._PATTERN, md
        )

    def handleMatch(self, m, data):
        """Handle the match."""
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Selector",
                has_attribute=True,
                attributes_val=4,
            )
            .set_varname()
            .set_className(class_name="taipy-selector", config_class="selector")
            .get_gui_value()
            .set_lov()
            .set_filter()
            .set_multiple()
            .set_default_value()
            .set_propagate()
            .build()
        )
