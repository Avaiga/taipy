# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import re
import typing as t
from typing import Any, List, Tuple

from markdown.preprocessors import Preprocessor as MdPreprocessor

from ..._warnings import _warn
from ..builder import _Builder
from .factory import _MarkdownFactory

if t.TYPE_CHECKING:
    from ...gui import Gui


class _Preprocessor(MdPreprocessor):
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
    # The default control type is 'text'.
    # ----------------------------------------------------------------------
    # Control in Markdown
    __CONTROL_RE = re.compile(r"<\|(.*?)\|>")
    # Opening tag
    __OPENING_TAG_RE = re.compile(r"<([0-9a-zA-Z\_\.]*)\|((?:(?!\|>).)*)\s*$")
    # Closing tag
    __CLOSING_TAG_RE = re.compile(r"^\s*\|([0-9a-zA-Z\_\.]*)>")
    # Link in Markdown
    __LINK_RE = re.compile(r"(\[[^\]]*?\]\([^\)]*?\))")
    # Split properties and control type
    __SPLIT_RE = re.compile(r"(?<!\\\\)\|")
    # Property syntax: '<prop_name>[=<prop_value>]'
    #   If <prop_value> is omitted:
    #     '<prop_name>' is equivalent to '<prop_name>=true'
    #     'not <prop_name>' is equivalent to '<prop_name>=false'
    #     'no', 'not', 'dont', 'don't' are equivalent in this context
    #  Note 1: 'not <prop_name>=<prop_value>' is an invalid syntax
    #  Note 2: Space characters after the equal sign are significative
    __PROPERTY_RE = re.compile(r"((?:don'?t|not?)\s+)?([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)\s*(?:=(.*))?$")

    # Error syntax detection regex
    __MISSING_LEADING_PIPE_RE = re.compile(r"^<[^|](.*?)\|>")

    _gui: "Gui"

    @staticmethod
    def extend(md, gui, priority):
        instance = _Preprocessor(md)
        md.preprocessors.register(instance, "taipy", priority)
        instance._gui = gui

    def _make_prop_pair(self, prop_name: str, prop_value: str) -> Tuple[str, str]:
        # Un-escape pipe character in property value
        return (prop_name, prop_value.replace("\\|", "|"))

    def _validate_line(self, line: str, line_count: int) -> bool:
        if _Preprocessor.__MISSING_LEADING_PIPE_RE.search(line) is not None:
            _warn(f"Missing leading pipe '|' in opening tag line {line_count}: '{line}'.")
            return False
        return True

    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        tag_stack = []
        for line_count, line in enumerate(lines, start=1):
            if not self._validate_line(line, line_count):
                continue
            new_line = ""
            last_index = 0
            # Opening tags
            m = _Preprocessor.__OPENING_TAG_RE.search(line)
            if m is not None:
                tag = "part"
                properties: List[Tuple[str, str]] = []
                if m.group(2):
                    tag, properties = self._process_control(m.group(2), line_count, tag)
                if tag in _MarkdownFactory._TAIPY_BLOCK_TAGS:
                    tag_stack.append((tag, line_count, m.group(1) or None))
                    new_line_delimeter = "\n" if line.startswith("<|") else "\n\n"
                    line = (
                        line[: m.start()]
                        + new_line_delimeter
                        + _MarkdownFactory._TAIPY_START
                        + tag
                        + _MarkdownFactory._START_SUFFIX
                    )
                    for property in properties:
                        prop_value = property[1].replace('"', '\\"')
                        line += f' {property[0]}="{prop_value}"'
                    line += _MarkdownFactory._TAIPY_END + new_line_delimeter
                else:
                    _warn(f"Failed to recognized block tag '{tag}' in line {line_count}. Check that you are closing the tag properly with '|>' if it is a control element.")  # noqa: E501
            # Other controls
            for m in _Preprocessor.__CONTROL_RE.finditer(line):
                control_name, properties = self._process_control(m.group(1), line_count)
                new_line += line[last_index : m.start()]
                control_text = _MarkdownFactory._TAIPY_START + control_name
                for property in properties:
                    prop_value = property[1].replace('"', '\\"')
                    control_text += f' {property[0]}="{prop_value}"'
                control_text += _MarkdownFactory._TAIPY_END
                new_line += control_text
                last_index = m.end()
            new_line = line if last_index == 0 else new_line + line[last_index:]
            # Add key attribute to links
            line = new_line
            new_line = ""
            last_index = 0
            for m in _Preprocessor.__LINK_RE.finditer(line):
                new_line += line[last_index : m.end()]
                new_line += "{: key=" + _Builder._get_key("link") + "}"
                last_index = m.end()
            new_line = line if last_index == 0 else new_line + line[last_index:]
            # Look for a closing tag
            m = _Preprocessor.__CLOSING_TAG_RE.search(new_line)
            if m is not None:
                if len(tag_stack):
                    open_tag, open_tag_line_count, open_tag_identifier = tag_stack.pop()
                    close_tag_identifier = m.group(1)
                    if close_tag_identifier and not open_tag_identifier:
                        _warn(
                            f"Missing opening '{open_tag}' tag identifier '{close_tag_identifier}' in line {open_tag_line_count}."  # noqa: E501
                        )
                    if open_tag_identifier and not close_tag_identifier:
                        _warn(
                            f"Missing closing '{open_tag}' tag identifier '{open_tag_identifier}' in line {line_count}."
                        )
                    if close_tag_identifier and open_tag_identifier and close_tag_identifier != open_tag_identifier:
                        _warn(
                            f"Unmatched '{open_tag}' tag identifier in line {open_tag_line_count} and line {line_count}."  # noqa: E501
                        )
                    new_line = (
                        new_line[: m.start()]
                        + _MarkdownFactory._TAIPY_START
                        + open_tag
                        + _MarkdownFactory._END_SUFFIX
                        + _MarkdownFactory._TAIPY_END
                        + "\n"
                        + new_line[m.end() :]
                    )
                else:
                    new_line = (
                        new_line[: m.start()]
                        + f"<div>No matching opened tag on line {line_count}</div>"
                        + new_line[m.end() :]
                    )
                    _warn(f"Line {line_count} has an unmatched closing tag.")
            # append the new line
            new_lines.append(new_line)
        # Issue #337: add an empty string at the beginning of new_lines list if there is not one
        # so that markdown extension would be able to render properly
        if new_lines and new_lines[0] != "":
            new_lines.insert(0, "")
        # Check for tags left unclosed (but close them anyway)
        for tag, line_no, _ in tag_stack:
            new_lines.append(
                _MarkdownFactory._TAIPY_START + tag + _MarkdownFactory._END_SUFFIX + _MarkdownFactory._TAIPY_END
            )
            _warn(f"Opened tag {tag} in line {line_no} is not closed.")
        return new_lines

    def _process_control(
        self, prop_string: str, line_count: int, default_control_name: str = _MarkdownFactory.DEFAULT_CONTROL
    ) -> Tuple[str, List[Tuple[str, str]]]:
        fragments = [f for f in _Preprocessor.__SPLIT_RE.split(prop_string) if f]
        control_name = None
        default_prop_name = None
        default_prop_value = None
        properties: List[Tuple[str, Any]] = []
        for fragment in fragments:
            if control_name is None and _MarkdownFactory.get_default_property_name(fragment):
                control_name = fragment
            elif control_name is None and default_prop_value is None:
                default_prop_value = fragment
            elif prop_match := _Preprocessor.__PROPERTY_RE.match(fragment):
                not_prefix = prop_match.group(1)
                prop_name = prop_match.group(2)
                val = prop_match.group(3)
                if not_prefix and val:
                    _warn(f"Negated property {prop_name} value ignored at {line_count}.")
                prop_value = "True"
                if not_prefix:
                    prop_value = "False"
                elif val:
                    prop_value = val
                properties.append(self._make_prop_pair(prop_name, prop_value))
            elif len(fragment) > 1 and fragment[0] == "{" and fragment[-1] == "}":
                properties.append(self._make_prop_pair(fragment[1:-1], fragment))
            else:
                _warn(f"Bad Taipy property format at line {line_count}: '{fragment}'.")
        if control_name is None:
            if properties and all(attribute != properties[0][0] for attribute in _MarkdownFactory._TEXT_ATTRIBUTES):
                control_name = properties[0][0]
                properties = properties[1:]
                _warn(f'Unrecognized control {control_name} at line {line_count}: "<|{prop_string}|>".')
            else:
                control_name = default_control_name
        if default_prop_value is not None:
            default_prop_name = _MarkdownFactory.get_default_property_name(control_name)
            # Set property only if it is not already defined
            if default_prop_name and default_prop_name not in [x[0] for x in properties]:
                properties.insert(0, self._make_prop_pair(default_prop_name, default_prop_value))
        return control_name, properties
