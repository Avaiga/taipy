import typing as t

from ..factory import Factory


class HtmlFactory(Factory):
    @staticmethod
    def create_element(gui, control_type: str, all_properties: t.Dict[str, str]) -> t.Tuple[str, str]:
        builder = Factory.CONTROL_BUILDERS[control_type](gui, control_type, all_properties)
        if not builder:
            return f"<div>INVALID SYNTAX - Control is '{control_type}'", "div"
        builder_str, element_name = builder.build_to_string()
        return builder_str, element_name
