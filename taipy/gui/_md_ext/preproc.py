import re
from typing import List

from markdown.preprocessors import Preprocessor as MdPreprocessor

from .factory import Factory


class Preprocessor(MdPreprocessor):
    _CONTROL_RE = re.compile(r"<\|(.*?)\|>")
    _SPLIT_RE = re.compile(r"(?<!\\\\)\|")

    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line in lines:
            new_line = ""
            last_index = 0
            for m in Preprocessor._CONTROL_RE.finditer(line):
                control_name, properties = self.process_line_iter(m)
                new_line += line[last_index : m.start()] + f"<|taipy.{control_name}{properties}|>"
                last_index = m.end()
            if last_index == 0:
                new_lines.append(line)
            else:
                new_lines.append(new_line + line[last_index:])
        return new_lines

    def process_line_iter(self, m):
        from ..gui import Gui

        fragments = Preprocessor._SPLIT_RE.split(m.group(1))
        control_name = None
        default_prop_name = None
        default_prop_value = None
        expr_hash = None
        properties = ""
        for fragment in fragments:
            if control_name is None and Factory.get_default_property_name(fragment):
                control_name = fragment
            elif control_name is None and default_prop_value is None:
                # Handle First Expression Fragment
                default_prop_value, expr_hash = Gui._get_instance().evaluate_expr(fragment)
                default_prop_value = expr_hash
            else:
                properties += "|" + fragment
        if control_name is None:
            control_name = "field"
        default_prop_name = Factory.get_default_property_name(control_name)
        if default_prop_value is not None:
            properties = f"|{default_prop_name}={default_prop_value}" + properties
        return control_name, properties
