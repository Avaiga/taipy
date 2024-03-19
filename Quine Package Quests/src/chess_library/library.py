from taipy.gui.extension import ElementLibrary, Element, ElementProperty, PropertyType

class ChessLibrary(ElementLibrary):
    def __init__(self) -> None:
        self.elements = {
            "board": Element(
                "data", 
                 {"data": ElementProperty(PropertyType.dynamic_string)},
                react_component="ChessBoard",
            ),
            "heatmap": Element(
                "data", 
                 {"data": ElementProperty(PropertyType.dynamic_string)},
                react_component="HeatMap",
            )
        }

    def get_name(self) -> str:
        return "chess_library"
    
    def get_elements(self) -> dict:
        return self.elements

    def get_scripts(self) -> list[str]:
        return ["front-end/dist/library.js"]