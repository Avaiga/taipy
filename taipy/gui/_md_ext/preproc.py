import re
from typing import List

from markdown.preprocessors import Preprocessor as MdPreprocessor

from .builder import Builder
from .factory import Factory


class Preprocessor(MdPreprocessor):
    # Legacy: _VAR_RE = re.compile(r"\[<\s*([a-zA-Z][\.a-zA-Z_$0-9]*)\s*>(\s*:\s*(.*?)\s*)?\]")
    _CONTROL_RE = re.compile(r"<\|(.*?)\|>")
    _SPLIT_RE = re.compile(r"(?<!\\\\)\|")
    # TODO: This prevents from using expressions, but keeps the compatibility
    # with legacy code. TO BE REMOVED
    _VARIABLE_RE = re.compile(r"{([a-zA-Z][\.a-zA-Z_$0-9]*)}")
    # Same as Factory._PROPERTY_RE. TODO: share or move to utils?
    _PROPERTY_RE = re.compile(r"([a-zA-Z][\.a-zA-Z_$0-9]*)\s*(?:=(.*))?")

    def run(self, lines: List[str]) -> List[str]:
        from ..gui import Gui

        new_lines = []
        for line in lines:
            new_line = ""
            last_index = 0
            for m in Preprocessor._CONTROL_RE.finditer(line):
                fragments = Preprocessor._SPLIT_RE.split(m.group(1))
                control_name = None
                default_prop_name = None
                default_prop_value = None
                var_index = None
                properties = ""
                for fragment in fragments:
                    if control_name is None and Factory.get_default_property_name(fragment):
                        control_name = fragment
                    elif control_name is None and default_prop_value is None:
                        # Is fragment a variable?
                        expr_match = Preprocessor._VARIABLE_RE.match(fragment)
                        if expr_match:
                            var_name = expr_match.group(1)
                            if var_name:
                                var_index = str(Gui._get_instance()._add_control(var_name))
                                default_prop_value = f"{{{var_name}({var_index})}}"
                        if var_name is None:
                            default_prop_value = fragment
                    else:
                        properties += "|" + fragment
                if control_name is None:
                    control_name = "field"
                default_prop_name = Factory.get_default_property_name(control_name)
                if default_prop_value is not None:
                    properties = f"|{default_prop_name}={default_prop_value}" + properties
                new_line += line[last_index : m.start()] + f"<|taipy.{control_name}{properties}|>"
                last_index = m.end()
            if last_index == 0:
                new_lines.append(line)
            else:
                new_lines.append(new_line + line[last_index:])
        return new_lines
