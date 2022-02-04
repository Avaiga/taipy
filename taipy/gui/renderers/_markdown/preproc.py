import re
import typing as t
import warnings
from typing import Any, List, Tuple

from markdown.preprocessors import Preprocessor as MdPreprocessor

from ..builder import Builder
from .factory import MarkdownFactory


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
    __CONTROL_RE = re.compile(r"<\|(.*?)\|>")
    # Opening tag
    __OPENING_TAG_RE = re.compile(r"<\|((?:(?!\|>).)*)\s*$")
    # Closing tag
    __CLOSING_TAG_RE = re.compile(r"^\s*\|>")
    # Link in Markdown
    __LINK_RE = re.compile(r"(\[[^\]]*?\]\([^\)]*?\))")
    # Split properties and control type
    __SPLIT_RE = re.compile(r"(?<!\\\\)\|")
    # Property syntax: '<prop_name>[=<prop_value>]'
    #   If <prop_value> is omitted:
    #     '<prop_name>' is equivalent to '<prop_name>=true'
    #     'not <prop_name>' is equivalent to '<prop_name>=false'
    #       'not', 'dont', 'don't' are equivalent in this context
    #  Note 1: 'not <prop_name>=<prop_value>' is an invalid syntax
    #  Note 2: Space characters after the equal sign are significative
    __PROPERTY_RE = re.compile(r"((?:don'?t|not)\s+)?([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)\s*(?:=(.*))?$")

    def _make_prop_pair(self, prop_name: str, prop_value: str) -> Tuple[str, str]:
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
                tag = "part"
                properties: List[Tuple[str, str]] = []
                if m.group(1):
                    tag, properties = self._process_control(m.group(1), line_count)
                if tag in MarkdownFactory._TAIPY_BLOCK_TAGS:
                    tag_queue.append((tag, line_count))
                    line = line[: m.start()] + "\n" + MarkdownFactory._TAIPY_START + tag + ".start"
                    for property in properties:
                        prop_value = property[1].replace('"', '\\"')
                        line += f' {property[0]}="{prop_value}"'
                    line += MarkdownFactory._TAIPY_END + "\n"
                else:
                    warnings.warn(f"Invalid tag name '{tag}' in line {line_count}")
            # Other controls
            for m in Preprocessor.__CONTROL_RE.finditer(line):
                control_name, properties = self._process_control(m.group(1), line_count)
                new_line += line[last_index : m.start()]
                control_text = MarkdownFactory._TAIPY_START + control_name
                for property in properties:
                    prop_value = property[1].replace('"', '\\"')
                    control_text += f' {property[0]}="{prop_value}"'
                control_text += MarkdownFactory._TAIPY_END
                new_line += control_text
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
            # Look for a closing tag
            m = Preprocessor.__CLOSING_TAG_RE.search(new_line)
            if m is not None:
                if len(tag_queue):
                    new_line = (
                        new_line[: m.start()]
                        + MarkdownFactory._TAIPY_START
                        + tag_queue.pop()[0]
                        + ".end"
                        + MarkdownFactory._TAIPY_END
                        + new_line[m.end() :]
                    )
                else:
                    new_line = (
                        new_line[: m.start()]
                        + f"<div>No matching opened tag on line {line_count}</div>"
                        + new_line[m.end() :]
                    )
                    warnings.warn(f"Line {line_count} has an unmatched closing tag")
            # append the new line
            new_lines.append(new_line)
        # Issue #337: add an empty string at the beginning of new_lines list if there is not one
        # so that markdown extension would be able to render properly
        if new_lines and new_lines[0] != "":
            new_lines.insert(0, "")
        # Check for tags left unclosed (but close them anyway)
        for tag, line_no in tag_queue:
            new_lines.append(MarkdownFactory._TAIPY_START + tag + ".end" + MarkdownFactory._TAIPY_END)
            warnings.warn(f"Opened tag {tag} in line {line_no} is not closed")
        return new_lines

    def _process_control(self, prop_string: str, line_count: int) -> Tuple[str, List[Tuple[str, str]]]:
        fragments = [f for f in Preprocessor.__SPLIT_RE.split(prop_string) if f]
        control_name = None
        default_prop_name = None
        default_prop_value = None
        properties: List[Tuple[str, Any]] = []
        for fragment in fragments:
            if control_name is None and MarkdownFactory.get_default_property_name(fragment):
                control_name = fragment
            elif control_name is None and default_prop_value is None:
                default_prop_value = fragment
            else:
                prop_match = Preprocessor.__PROPERTY_RE.match(fragment)
                if prop_match:
                    not_prefix = prop_match.group(1)
                    prop_name = prop_match.group(2)
                    val = prop_match.group(3)
                    if not_prefix and val:
                        warnings.warn(f"Negated property {prop_name} value ignored at {line_count}")
                    prop_value = "True"
                    if not_prefix:
                        prop_value = "False"
                    elif val:
                        prop_value = val
                    properties.append(self._make_prop_pair(prop_name, prop_value))
                else:
                    warnings.warn(f"Bad Taipy property format at line {line_count}: '{fragment}'")

        if control_name is None:
            control_name = MarkdownFactory.DEFAULT_CONTROL
        if default_prop_value is not None:
            default_prop_name = MarkdownFactory.get_default_property_name(control_name)
            # Set property only if it is not already defined
            if default_prop_name and default_prop_name not in [x[0] for x in properties]:
                properties.insert(0, self._make_prop_pair(default_prop_name, default_prop_value))
        return control_name, properties
