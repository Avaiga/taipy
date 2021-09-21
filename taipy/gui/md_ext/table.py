from markdown.inlinepatterns import InlineProcessor

from .builder import MarkdownBuilder


# The table pattern also handles the [<var>] construct
class TablePattern(InlineProcessor):

    # group(1): var_name
    # group(2): var_id
    # group(3): table+attributes
    # group(4): attributes
    _PATTERN = r"\[(?:TaIpY([a-zA-Z][\.a-zA-Z_$0-9]*)\{(\d+)\})?(table\s*(?:\:\s*(.*?))?)?\s*\]"

    @staticmethod
    def extendMarkdown(md):
        md.inlinePatterns["taipy-table"] = TablePattern(TablePattern._PATTERN, md)

    def handleMatch(self, m, data):
        """Handle the match."""
        return (
            MarkdownBuilder(
                m=m,
                el_element_name="Table",
                has_attribute=True,
                attributes_val=4,
            )
            .set_varname()
            .set_className(class_name="taipy-table", config_class="table")
            .set_table_pagesize()
            .build()
        )
