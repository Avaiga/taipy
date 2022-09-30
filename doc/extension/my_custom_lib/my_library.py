 
from taipy.gui.extension import ElementLibrary, Element, ElementProperty, PropertyType

class MyLibrary(ElementLibrary):
    def get_name(self) -> str:
        return "my_custom"
    def get_elements(self) -> dict:
        return ({
            "label":
            Element("value", {
                "value": ElementProperty(PropertyType.dynamic_string)
                },
                react_component="MyLabel"
            )
            })
    def get_scripts(self) -> list[str]:
        # Only one JavaScript bundle for this library.
        return ["my_custom_lib/webui/dist/MyCustom.js"]
