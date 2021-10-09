import re
import typing as t
import warnings
from typing import Any, List, Tuple

from markdown.preprocessors import Preprocessor as MdPreprocessor


class Preprocessor(MdPreprocessor):
    # ----------------------------------------------------------------------
    # Finds, in the Mardwodn text, control declaration constructs:
    #     <|<some value>|>
    # or
    #     <|<some value>|<control_type>|>
    # or
    #     <|<some value>|<control_type>|<prop_name[=propvalue]>>
    # or
    #     <|<control_type>|<prop_name[=propvalue]>>
    #
    # These constructs are converted a fragment that the ControlPattern
    # processes to create the components that get generated.
    #     <control_type> prop_name="prop_value" ...
    # Note that if a value is provided before the control_type, it is set
    # as the default property value for that control type.
    # The default control type is 'field'.
    # ----------------------------------------------------------------------
    # Control in Markdown
    _CONTROL_RE = re.compile(r"<\|(.*?)\|>")
    # Split properties and control type
    _SPLIT_RE = re.compile(r"(?<!\\\\)\|")
    # Property syntax: '<prop_name>[=<prop_value>]'
    #   If <prop_value> is ommitted:
    #     '<prop_name>' is equivalent to '<prop_name>=true'
    #     'not <prop_name>' is equivalent to '<prop_name>=false'
    #       'not', 'dont', 'don't' are equivalent in this context
    #  Note 1: 'not <prop_name>=<prop_value>' is an invalid syntax
    #  Note 2: Space characters after the equal sign are significative
    _PROPERTY_RE = re.compile(r"((?:don'?t|not)\s+)?([a-zA-Z][\.a-zA-Z_$0-9]*)\s*(?:=(.*))?")

    def _make_prop_pair(self, prop_name: t.Optional[str], prop_value: str) -> tuple[t.Optional[str], str]:
        # Un-escape pipe character in property value
        return (prop_name, prop_value.replace("\\|", "|"))

    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line_count, line in enumerate(lines, start=1):
            new_line = ""
            last_index = 0
            for m in Preprocessor._CONTROL_RE.finditer(line):
                control_name, properties = self._process_control(m, line_count)
                new_line += line[last_index : m.start()] + "TaIpY:" + control_name
                for property in properties:
                    prop_value = property[1].replace('"', '\\"')
                    new_line += f' {property[0]}="{prop_value}"'
                new_line += ":tAiPy"
                last_index = m.end()
            if last_index == 0:
                new_lines.append(line)
            else:
                new_lines.append(new_line + line[last_index:])
        return new_lines

    def _process_control(self, m: re.Match, line_count: int) -> Tuple[str, Any]:
        fragments = Preprocessor._SPLIT_RE.split(m.group(1))
        control_name = None
        default_prop_name = None
        default_prop_value = None
        properties = []
        for fragment in fragments:
            from .factory import Factory

            if control_name is None and Factory.get_default_property_name(fragment):
                control_name = fragment
            elif control_name is None and default_prop_value is None:
                from ..gui import Gui

                # Handle First Expression Fragment
                default_prop_value = Gui._get_instance().evaluate_expr(fragment)
            else:
                prop_match = Preprocessor._PROPERTY_RE.match(fragment)
                if not prop_match or (prop_match.group(1) and prop_match.group(3)):
                    warnings.warn(f"Bad Taipy property format at line {line_count}: '{fragment}'")
                else:
                    from ..gui import Gui

                    prop_value = "True"
                    if prop_match.group(1):
                        prop_value = "False"
                    elif prop_match.group(3):
                        prop_value = prop_match.group(3)
                    prop_value = Gui._get_instance().evaluate_expr(prop_value)
                    properties.append(self._make_prop_pair(prop_match.group(2), prop_value))
        if control_name is None:
            control_name = "field"
        if default_prop_value is not None:
            default_prop_name = Factory.get_default_property_name(control_name)
            properties.insert(0, self._make_prop_pair(default_prop_name, default_prop_value))
        return control_name, properties
