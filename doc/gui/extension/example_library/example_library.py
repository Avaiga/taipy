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

from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType


class ExampleLibrary(ElementLibrary):
    def __init__(self) -> None:
        # Initialize the set of visual elements for this extension library
        self.elements = {
            # A static element that displays its properties in a fraction
            "fraction": Element(
                "numerator",
                {
                    "numerator": ElementProperty(PropertyType.number),
                    "denominator": ElementProperty(PropertyType.number),
                },
                render_xhtml=ExampleLibrary._fraction_render,
            ),
            # A dynamic element that decorates its value
            "label": Element(
                "value",
                {"value": ElementProperty(PropertyType.dynamic_string)},
                # The name of the React component (ColoredLabel) that implements this custom
                # element, exported as ExampleLabel in front-end/src/index.ts
                react_component="ExampleLabel",
            ),
        }

    # The implementation of the rendering for the "fraction" static element
    @staticmethod
    def _fraction_render(props: dict) -> str:
        # Get the property values
        numerator = props.get("numerator")
        denominator = props.get("denominator")
        # No denominator or numerator is 0: display the numerator
        if denominator is None or int(numerator) == 0:  # type: ignore[arg-type]
            return f"<span>{numerator}</span>"
        # Denominator is zero: display infinity
        if int(denominator) == 0:
            return '<span style="font-size: 1.6em">&#8734;</span>'
        # 'Normal' case
        return f"<span><sup>{numerator}</sup>/<sub>{denominator}</sub></span>"

    def get_name(self) -> str:
        return "example"

    def get_elements(self) -> dict:
        return self.elements

    def get_scripts(self) -> list[str]:
        # Only one JavaScript bundle for this library.
        return ["front-end/dist/exampleLibrary.js"]
