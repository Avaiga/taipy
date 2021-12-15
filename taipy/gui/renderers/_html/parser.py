import re
import typing as t
from html.parser import HTMLParser

from .factory import HtmlFactory


class TaipyHTMLParser(HTMLParser):

    __TAIPY_NAMESPACE_RE = re.compile(r"taipy:([a-zA-Z\_]*)")

    def __init__(self):
        super().__init__()
        self.body = ""
        self.head = []
        self.taipy_tag = None
        self.tag_mapping = {}
        self.is_body = True
        self.head_tag = None

    # @override
    def handle_starttag(self, tag, props) -> None:
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
            self.taipy_tag = TaipyTag(m.group(1), props)
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
        tp_string, tp_element_name = self.taipy_tag.parse()
        self.append_data(tp_string)
        self.tag_mapping[f"taipy:{self.taipy_tag.control_type}"] = tp_element_name
        self.taipy_tag = None

    def get_jsx(self) -> str:
        return self.body


class TaipyTag(object):
    def __init__(self, tag_name: str, properties: t.List[t.Tuple[str, str]]) -> None:
        self.control_type = tag_name
        self.properties = {}
        for prop in properties:
            self.properties[prop[0]] = prop[1]
        self.has_set_value = False

    def set_value(self, value: str) -> bool:
        if self.has_set_value:
            return False
        property_name = HtmlFactory.get_default_property_name(self.control_type)
        if property_name is not None:
            self.properties[property_name] = value
        self.has_set_value = True
        return True

    def parse(self) -> t.Tuple[str, str]:
        from ...gui import Gui

        gui = Gui._get_instance()
        for k, v in self.properties.items():
            self.properties[k] = gui._evaluate_expr(v) if v is not None else "true"
        return HtmlFactory.create_element(self.control_type, self.properties)
