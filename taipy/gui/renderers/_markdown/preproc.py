import re
import typing as t
import warnings
from typing import Any, List, Tuple

from markdown.preprocessors import Preprocessor as MdPreprocessor

from .factory import MarkdownFactory
from ..builder import Builder


class Preprocessor(MdPreprocessor):
    # ----------------------------------------------------------------------
    # Finds, in the Markdown text, control declaration constructs:
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
    __CONTROL_RE = re.compile(r"<\|([^<>]*)(>?)")
    # Closing tag
    __CLOSING_TAG_RE = re.compile(r"^\s*(\|>)")
    # Opening tag
    __OPENING_TAG_RE = re.compile(r"(<\|)\s*$")
    # Link in Markdown
    __LINK_RE = re.compile(r"(\[[^\]]*?\]\([^\)]*?\))")
    # Split properties and control type
    __SPLIT_RE = re.compile(r"(?<!\\\\)\|")
    # Property syntax: '<prop_name>[=<prop_value>]'
    #   If <prop_value> is ommitted:
    #     '<prop_name>' is equivalent to '<prop_name>=true'
    #     'not <prop_name>' is equivalent to '<prop_name>=false'
    #       'not', 'dont', 'don't' are equivalent in this context
    #  Note 1: 'not <prop_name>=<prop_value>' is an invalid syntax
    #  Note 2: Space characters after the equal sign are significative
    __PROPERTY_RE = re.compile(r"((?:don'?t|not)\s+)?([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)\s*(?:=(.*))?")

    def _make_prop_pair(self, prop_name: t.Optional[str], prop_value: str) -> tuple[t.Optional[str], str]:
        # Un-escape pipe character in property value
        return (prop_name, prop_value.replace("\\|", "|"))

    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        tag_queue = []
        for line_count, line in enumerate(lines, start=1):
            new_line = ""
            last_index = 0
            # Opening tags
            m = Preprocessor.__OPENING_TAG_RE.search(line)
            if m is not None:
                tag_queue.append("part")
                line = (
                    line[: m.start()]
                    + "\n"
                    + MarkdownFactory._TAIPY_START
                    + "part.start"
                    + MarkdownFactory._TAIPY_END
                    + "\n"
                    + line[m.end() :]
                )
            # all other components
            for m in Preprocessor.__CONTROL_RE.finditer(line):
                start_tag = len(m.group(2)) == 0  # tag not closed
                control_name, properties = self._process_control(m, line_count)
                new_line += line[last_index : m.start()]
                local_line = MarkdownFactory._TAIPY_START + control_name
                block = False
                if start_tag:
                    if control_name in MarkdownFactory._TAIPY_BLOCK_TAGS:
                        local_line += ".start"
                        tag_queue.append(control_name)
                        block = True
                    else:
                        warnings.warn(f"Line {line_count} tag {control_name} is not properly closed")
                for property in properties:
                    prop_value = property[1].replace('"', '\\"')
                    local_line += f' {property[0]}="{prop_value}"'
                local_line += MarkdownFactory._TAIPY_END
                if block:
                    local_line = "\n" + local_line + "\n"
                new_line += local_line
                last_index = m.end()
            new_line = line if last_index == 0 else new_line + line[last_index:]
            # Add key attribute to links
            line = new_line
            new_line = ""
            last_index = 0
            for m in Preprocessor.__LINK_RE.finditer(line):
                new_line += line[last_index : m.end()]
                new_line += "{: key=" + Builder._get_key("link") + "}"
                last_index = m.end()
            new_line = line if last_index == 0 else new_line + line[last_index:]
            # check for closing tag
            m = Preprocessor.__CLOSING_TAG_RE.search(new_line)
            if m is not None:
                if len(tag_queue):
                    new_line = (
                        new_line[: m.start()]
                        + MarkdownFactory._TAIPY_START
                        + tag_queue.pop()
                        + ".end"
                        + MarkdownFactory._TAIPY_END
                        + new_line[m.end() :]
                    )
                else:
                    new_line = (
                        new_line[: m.start()] + f"<div>No matching tag line {line_count}</div>" + new_line[m.end() :]
                    )
                    warnings.warn(f"Line {line_count} has a closing tag not matching")
            # append the new line
            new_lines.append(new_line)
        # issue #337: add an empty string at the beginning of new_lines list if there is not one
        # so that markdown extension would be able to render properly
        if new_lines and new_lines[0] != "":
            new_lines.insert(0, "")
        # Check for unfinished tags
        for tag in tag_queue:
            new_lines.append(MarkdownFactory._TAIPY_START + tag + ".end" + MarkdownFactory._TAIPY_END)
            warnings.warn(f"tag {tag} was not closed")
        return new_lines

    def _process_control(self, m: re.Match, line_count: int) -> Tuple[str, Any]:
        fragments = [f for f in Preprocessor.__SPLIT_RE.split(m.group(1)) if f]
        control_name = None
        default_prop_name = None
        default_prop_value = None
        properties = []
        for fragment in fragments:
            from .factory import MarkdownFactory

            if control_name is None and MarkdownFactory.get_default_property_name(fragment):
                control_name = fragment
            elif control_name is None and default_prop_value is None:
                from ...gui import Gui

                # Handle First Expression Fragment
                default_prop_value = Gui._get_instance().evaluate_expr(fragment)
            else:
                prop_match = Preprocessor.__PROPERTY_RE.match(fragment)
                if not prop_match or (prop_match.group(1) and prop_match.group(3)):
                    warnings.warn(f"Bad Taipy property format at line {line_count}: '{fragment}'")
                else:
                    from ...gui import Gui

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
            default_prop_name = MarkdownFactory.get_default_property_name(control_name)
            properties.insert(0, self._make_prop_pair(default_prop_name, default_prop_value))
        return control_name, properties
