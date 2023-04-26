# Copyright 2023 Avaiga Private Limited
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
from html.parser import HTMLParser

from ..._warnings import _warn
from .factory import _HtmlFactory


class _TaipyHTMLParser(HTMLParser):
    __TAIPY_NAMESPACE_RE = re.compile(r"([a-zA-Z\_]+):([a-zA-Z\_]*)")

    def __init__(self, gui):
        super().__init__()
        self._gui = gui
        self.body = ""
        self.head = []
        self.taipy_tag = None
        self.tag_mapping = {}
        self.is_body = True
        self.head_tag = None
        self._line_count = 0
        self._tag_queue = []

    # @override
    def handle_starttag(self, tag, props) -> None:
        self._tag_queue.append((tag, self._line_count))
        if tag == "html":
            return
        if self.head_tag is not None:
            self.head.append(self.head_tag)
            self.head_tag = None
        if self.taipy_tag is not None:
            self.parse_taipy_tag()
        if tag == "head":
            self.is_body = False
        elif tag == "body":
            self.is_body = True
        elif m := self.__TAIPY_NAMESPACE_RE.match(tag):
            self.taipy_tag = _TaipyTag(m.group(1), m.group(2), props)
        elif not self.is_body:
            head_props = {prop[0]: prop[1] for prop in props}
            self.head_tag = {"tag": tag, "props": head_props, "content": ""}
        else:
            self.append_data(str(self.get_starttag_text()))

    # @override
    def handle_data(self, data: str) -> None:
        data = data.strip()
        if data and self.taipy_tag is not None and self.taipy_tag.set_value(data):
            self.parse_taipy_tag()
        elif not self.is_body and self.head_tag is not None:
            self.head_tag["content"] = data
        else:
            self.append_data(data)

    # @override
    def handle_endtag(self, tag) -> None:
        if not self._tag_queue:
            _warn(f"Closing '{tag}' at line {self._line_count} is missing an opening tag.")
        else:
            opening_tag, opening_tag_line = self._tag_queue.pop()
            if opening_tag != tag:
                _warn(
                    f"Opening tag '{opening_tag}' at line {opening_tag_line} has no matching closing tag '{tag}' at line {self._line_count}."
                )
        if tag in ["head", "body", "html"]:
            return
        if self.taipy_tag is not None:
            self.parse_taipy_tag()
        if not self.is_body:
            self.head.append(self.head_tag)
            self.head_tag = None
        elif tag in self.tag_mapping:
            self.append_data(f"</{self.tag_mapping[tag]}>")
        else:
            self.append_data(f"</{tag}>")

    def append_data(self, data: str) -> None:
        if self.is_body:
            self.body += data

    def parse_taipy_tag(self) -> None:
        tp_string, tp_element_name = self.taipy_tag.parse(self._gui)
        self.append_data(tp_string)
        self.tag_mapping[f"taipy:{self.taipy_tag.control_type}"] = tp_element_name
        self.taipy_tag = None

    def get_jsx(self) -> str:
        return self.body

    def feed_data(self, data: str):
        data_lines = data.split("\n")
        for line, data_line in enumerate(data_lines):
            self._line_count = line + 1
            self.feed(data_line)
        while self._tag_queue:
            opening_tag, opening_tag_line = self._tag_queue.pop()
            _warn(f"Opening tag '{opening_tag}' at line {opening_tag_line} has no matching closing tag.")


class _TaipyTag(object):
    def __init__(self, namespace: str, tag_name: str, properties: t.List[t.Tuple[str, str]]) -> None:
        self.namespace = namespace
        self.control_type = tag_name
        self.properties = {prop[0]: prop[1] for prop in properties}
        self.has_set_value = False

    def set_value(self, value: str) -> bool:
        if self.has_set_value:
            return False
        property_name = _HtmlFactory.get_default_property_name(f"{self.namespace}.{self.control_type}")
        # Set property only if it is not already defined
        if property_name and property_name not in self.properties.keys():
            self.properties[property_name] = value
        self.has_set_value = True
        return True

    def parse(self, gui) -> t.Tuple[str, str]:
        for k, v in self.properties.items():
            self.properties[k] = v if v is not None else "true"
        # allow usage of 'class' property in html taipy tag
        if "class" in self.properties and "class_name" not in self.properties:
            self.properties["class_name"] = self.properties["class"]
        return _HtmlFactory.create_element(gui, self.namespace, self.control_type, self.properties)
