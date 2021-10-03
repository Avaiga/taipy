import re
from typing import List

from markdown.preprocessors import Preprocessor as MdPreprocessor

from .builder import Builder
from .factory import Factory


class Preprocessor(MdPreprocessor):
    # ----------------------------------------------------------------------
    # Searchs, in the Mardwodn text, control declaration constructs:
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
    # TODO: This prevents from using expressions, but keeps the compatibility
    # with legacy code. TO BE REMOVED
    _VARIABLE_RE = re.compile(r"{([a-zA-Z][\.a-zA-Z_$0-9]*)}")
    # Property syntax: '<prop_name>[=<prop_value>]'
    #   If <prop_value> is ommitted:
    #     '<prop_name>' is equivalent to '<prop_name>=true'
    #     '!<prop_name>' is equivalent to '<prop_name>=false'
    #  Note 1: '!<prop_name>=<prop_value>' is an invalid syntax
    #  Note 2: Space characters after the equal sign are significative
    _PROPERTY_RE = re.compile(r"(!)?([a-zA-Z][\.a-zA-Z_$0-9]*)\s*(?:=(.*))?")


    def _make_prop_pair(self, prop_name: str, prop_value: str) -> tuple[str, str]:
        # Un-escape pipe character in property value
        return (prop_name, prop_value.replace("\\|", "|"))

    def run(self, lines: List[str]) -> List[str]:
        from ..gui import Gui

        line_count = 0
        new_lines = []
        for line in lines:
            line_count += 1
            new_line = ""
            last_index = 0
            for m in Preprocessor._CONTROL_RE.finditer(line):
                fragments = Preprocessor._SPLIT_RE.split(m.group(1))
                control_name = None
                default_prop_name = None
                default_prop_value = None
                properties = []
                for fragment in fragments:
                    if control_name is None and Factory.get_default_property_name(fragment):
                        control_name = fragment
                    elif control_name is None and default_prop_value is None:
                        default_prop_value = fragment
                    else:
                        prop_match = Preprocessor._PROPERTY_RE.match(fragment)
                        if not prop_match or (prop_match.group(1) and prop_match.group(3)):
                            print(f"Bad Taipy property format at line {line_count}: '{fragment}'", flush=True)
                        elif prop_match.group(1):
                            properties.append(self._make_prop_pair(prop_match.group(2), 'false'))
                        elif prop_match.group(3):
                            properties.append(self._make_prop_pair(prop_match.group(2), prop_match.group(3)))
                        else:
                            properties.append(self._make_prop_pair(prop_match.group(2), 'true'))
                if control_name is None:
                    control_name = "field"
                if default_prop_value is not None:
                    default_prop_name = Factory.get_default_property_name(control_name)
                    properties.insert(0, self._make_prop_pair(default_prop_name, default_prop_value))
                new_line += line[last_index : m.start()] + "TaIpY:" + control_name
                for property in properties:
                    # Bind variable if one is found
                    # We keep here the compatibility with legacy code: the variable is
                    # bound if and only if the property value is "{var_name}"
                    # There could be plenty of variables in this fragment...
                    # TODO: Actually, FLE thinks all this is useless...
                    prop_value = property[1]
                    var_match = Preprocessor._VARIABLE_RE.match(prop_value)
                    if var_match:
                        var_name = var_match.group(1)
                        # Register variable to the Gui
                        if var_name:
                            Gui._get_instance()._add_control(var_name)
                    else:
                        prop_value = property[1].replace("\"", "\\\"")
                    new_line += f" {property[0]}=\"{prop_value}\""
                new_line += ":tAiPy"
                last_index = m.end()
            if last_index == 0:
                new_lines.append(line)
            else:
                new_lines.append(new_line + line[last_index:])
        return new_lines
