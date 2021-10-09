import re
import xml.etree.ElementTree as ET
from operator import attrgetter

from markdown.treeprocessors import Treeprocessor

from ..utils import _MapDictionary
from .utils import _get_columns_dict

pattern = re.compile("(<Taipy.*/>|<Taipy.*</Taipy.*>)")


class TaipyTreeprocessor(Treeprocessor):
    def __init__(self, md, config):
        super().__init__(md)

    @staticmethod
    def extendMarkdown_i(md):
        md.treeprocessors.register(TaipyTreeprocessor(md, {}), "Taipy-tree", 30)

    def run(self, root):
        from ..gui import Gui

        for node in root.findall(".//"):
            if "<Taipy" in node.text:
                text = ""
                end = 0
                for match in pattern.finditer(node.text):
                    text += node.text[end : match.start()]
                    html = ET.fromstring(match.group())
                    html.tag = html.tag[5:]
                    var_name = html.get("value")
                    value = None
                    if var_name and Gui._get_instance().bind_var(var_name.split(sep=".")[0]):
                        html.set("value", "{!" + var_name.replace(".", "__") + "!}")
                        html.set("tp_varname", var_name.replace(".", "__"))
                        _instance = str(Gui._get_instance()._add_control(var_name))
                        html.set("key", var_name + str(_instance))
                        value = attrgetter(var_name)(Gui._get_instance()._values)
                    prop = html.get("properties")
                    if prop and Gui._get_instance().bind_var(prop):
                        prop_dict = getattr(Gui._get_instance(), prop)
                        if not isinstance(prop_dict, _MapDictionary):
                            raise Exception(
                                f"Can't find properties configuration dictionary for {prop}!"
                                f" Please review your GUI templates!"
                            )
                        # Iterate through properties_dict and append to self.attributes
                        prop_dict["columns"] = _get_columns_dict(
                            value,
                            prop_dict["columns"] if "columns" in prop_dict else html.get("columns"),
                            prop_dict["date_format"] if "date_format" in prop_dict else html.get("date_format"),
                        )
                        for k, v in prop_dict.items():
                            if isinstance(v, bool):
                                v = "{!" + str(v).lower() + "!}"
                            elif not isinstance(v, str):
                                v = "{!" + str(v) + "!}"
                            # camelCase the property names
                            k = k.replace("_", " ").title().replace(" ", "")
                            k = k[0].lower() + k[1:]
                            html.set(k, v)
                    text += ET.tostring(html, encoding="unicode", method="xml")
                    end = match.end()
                text += node.text[end:]
                node.text = text
