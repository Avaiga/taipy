from ..factory import _Factory


class _MarkdownFactory(_Factory):
    # Taipy Markdown tags
    _TAIPY_START = "TaIpY:"
    _TAIPY_END = ":tAiPy"

    _TAIPY_BLOCK_TAGS = ["layout", "part", "expandable", "dialog", "pane"]

    @staticmethod
    def create_element(gui, control_type: str, all_properties: str) -> str:
        # Create properties dict from all_properties
        property_pairs = _Factory._PROPERTY_RE.findall(all_properties)
        properties = {property[0]: property[1] for property in property_pairs}
        if builder := _Factory.CONTROL_BUILDERS[control_type](gui, control_type, properties):
            return builder.el
        else:
            return f"<|INVALID SYNTAX - Control is '{control_type}'|>"
