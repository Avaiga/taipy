from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder

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

    def handleMatch(self, m, data):
        # if Field Input
        if m.group(3):
            return (
                MarkdownBuilder(
                    m=m,
                    el_element_name="Input",
                    has_attribute=False,
                    default_value="<empty>",
                )
                .set_type("text")
                .get_app_value()
                .set_varname()
                .set_default_value()
                .set_className(class_name="taipy-field", config_class="input")
                .build()
            )
        # else Field
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Field",
                has_attribute=False,
                default_value="<empty>",
            )
            .get_app_value()
            .set_varname()
            .set_default_value()
            .set_className(class_name="taipy-var", config_class="field")
            .set_dataType()
            .build()
        )
