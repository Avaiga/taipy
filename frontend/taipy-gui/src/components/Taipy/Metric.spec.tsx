/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React, {act} from "react";
import {render, waitFor, RenderResult} from "@testing-library/react";
import "@testing-library/jest-dom";
import {ThemeProvider} from '@mui/material/styles';
import {createTheme} from '@mui/material/styles';

import Metric from "./Metric";

const template = {
    "layout": {
        "colorscale": {
            "diverging": [
                [
                    0,
                    "#8e0152"
                ],
                [
                    0.1,
                    "#c51b7d"
                ],
                [
                    0.2,
                    "#de77ae"
                ],
                [
                    0.3,
                    "#f1b6da"
                ],
                [
                    0.4,
                    "#fde0ef"
                ],
                [
                    0.5,
                    "#f7f7f7"
                ],
                [
                    0.6,
                    "#e6f5d0"
                ],
                [
                    0.7,
                    "#b8e186"
                ],
                [
                    0.8,
                    "#7fbc41"
                ],
                [
                    0.9,
                    "#4d9221"
                ],
                [
                    1,
                    "#276419"
                ]
            ],
            "sequential": [
                [
                    0,
                    "#0d0887"
                ],
                [
                    0.1111111111111111,
                    "#46039f"
                ],
                [
                    0.2222222222222222,
                    "#7201a8"
                ],
                [
                    0.3333333333333333,
                    "#9c179e"
                ],
                [
                    0.4444444444444444,
                    "#bd3786"
                ],
                [
                    0.5555555555555556,
                    "#d8576b"
                ],
                [
                    0.6666666666666666,
                    "#ed7953"
                ],
                [
                    0.7777777777777778,
                    "#fb9f3a"
                ],
                [
                    0.8888888888888888,
                    "#fdca26"
                ],
                [
                    1,
                    "#f0f921"
                ]
            ],
            "sequentialminus": [
                [
                    0,
                    "#0d0887"
                ],
                [
                    0.1111111111111111,
                    "#46039f"
                ],
                [
                    0.2222222222222222,
                    "#7201a8"
                ],
                [
                    0.3333333333333333,
                    "#9c179e"
                ],
                [
                    0.4444444444444444,
                    "#bd3786"
                ],
                [
                    0.5555555555555556,
                    "#d8576b"
                ],
                [
                    0.6666666666666666,
                    "#ed7953"
                ],
                [
                    0.7777777777777778,
                    "#fb9f3a"
                ],
                [
                    0.8888888888888888,
                    "#fdca26"
                ],
                [
                    1,
                    "#f0f921"
                ]
            ]
        }
    }
}

const colorMap = {
    20: "red",
    40: null,
    60: "blue",
    80: null
};

const darkTemplate = {
    layout: {
        colorscale: {
            diverging: [
                [0, "#8e0152"],
                [0.1, "#c51b7d"],
                [0.2, "#de77ae"],
                [0.3, "#f1b6da"],
                [0.4, "#fde0ef"],
                [0.5, "#f7f7f7"],
                [0.6, "#e6f5d0"],
                [0.7, "#b8e186"],
                [0.8, "#7fbc41"],
                [0.9, "#4d9221"],
                [1, "#276419"]
            ],
            sequential: [
                [0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1, "#f0f921"]
            ],
            sequentialminus: [
                [0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1, "#f0f921"]
            ]
        },
        paper_bgcolor: "rgb(31,47,68)",
    }
}

const lightTemplate = {
    layout: {
        colorscale: {
            diverging: [
                [0, "#053061"],
                [0.1, "#2166ac"],
                [0.2, "#4393c3"],
                [0.3, "#92c5de"],
                [0.4, "#d1e5f0"],
                [0.5, "#f7f7f7"],
                [0.6, "#fddbc7"],
                [0.7, "#f4a582"],
                [0.8, "#d6604d"],
                [0.9, "#b2182b"],
                [1, "#67001f"]
            ],
            sequential: [
                [0, "#f7fcf5"],
                [0.1111111111111111, "#e5f5e0"],
                [0.2222222222222222, "#c7e9c0"],
                [0.3333333333333333, "#a1d99b"],
                [0.4444444444444444, "#74c476"],
                [0.5555555555555556, "#41ab5d"],
                [0.6666666666666666, "#238b45"],
                [0.7777777777777778, "#006d2c"],
                [0.8888888888888888, "#00441b"],
                [1, "#000000"]
            ],
            sequentialminus: [
                [0, "#f7fcf5"],
                [0.1111111111111111, "#e5f5e0"],
                [0.2222222222222222, "#c7e9c0"],
                [0.3333333333333333, "#a1d99b"],
                [0.4444444444444444, "#74c476"],
                [0.5555555555555556, "#41ab5d"],
                [0.6666666666666666, "#238b45"],
                [0.7777777777777778, "#006d2c"],
                [0.8888888888888888, "#00441b"],
                [1, "#000000"]
            ]
        },
        paper_bgcolor: "rgb(255,255,255)",
    }
}

describe("Metric Component", () => {
    it("renders", async () => {
        const {getByTestId} = render(<Metric testId="test-id"/>);
        const elt = getByTestId("test-id");
        expect(elt.tagName).toBe("DIV");
    })

    it("displays the right info for class", async () => {
        const {getByTestId} = render(<Metric testId="test-id" className={'taipy-gauge'}/>);
        const elt = getByTestId('test-id');
        expect(elt).toHaveClass('taipy-gauge');
    })

    it("sets the title when provided", async () => {
        const title = "Test Title";
        let container: RenderResult | null = null;
        container = render(<Metric title={title}/>);
        await waitFor(() => {
            const titleElement = container!.container.querySelector('.gtitle');
            if (!titleElement) {
                throw new Error('Title element not found');
            }
            expect(titleElement.textContent).toContain(title);
        });
    });

    it('logs an error when template prop is a malformed JSON string', () => {
        const consoleSpy = jest.spyOn(console, 'info');
        const malformedJson = "{ key: 'value'";
        render(<Metric template={malformedJson}/>);
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Error while parsing Metric.template'));
        consoleSpy.mockRestore();
    });

    it('logs an error when colorMap prop is a malformed JSON string', () => {
        const consoleSpy = jest.spyOn(console, 'info');
        const malformedJson = "{ key: 'value'"; // missing closing brace
        render(<Metric colorMap={malformedJson}/>);
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Error parsing color_map value (metric)'));
        consoleSpy.mockRestore();
    });

    it("sets the template when provided", async () => {
        let container: RenderResult | null = null;
        container = render(<Metric template={JSON.stringify(template)}/>);
        await waitFor(() => {
            const elmWithTpl = container!.container.querySelector('.user-select-none')
            expect(elmWithTpl).toBeInTheDocument()
        })
    });

    it('processes colorMap prop correctly', async () => {
        render(<Metric colorMap={JSON.stringify(colorMap)}/>);
        await waitFor(() => {
            const elts = document.querySelectorAll('.bg-arc');
            const redElt = Array.from(elts[1].children);
            const redEltHasRedFill = redElt.some((elt) => (elt as HTMLElement).style.fill === 'rgb(255, 0, 0)');
            expect(redEltHasRedFill).toBeTruthy();

            const blueElt = Array.from(elts[2].children);
            const blueEltHasBlueFill = blueElt.some((elt) => (elt as HTMLElement).style.fill === 'rgb(0, 0, 255)');
            expect(blueEltHasBlueFill).toBeTruthy();
        });
    });

    it('processes delta prop correctly when delta is defined', async () => {
        render(<Metric delta={10} testId="test-id"/>);
        await waitFor(() => {
            const elt = document.querySelector('.delta');
            if (elt) {
                expect(elt.textContent).toContain('10');
            } else {
                throw new Error('Element with class .delta not found');
            }
        });
    });

    it('processes type and threshold props correctly when type is linear', async () => {
        render(<Metric type="linear" threshold={50} testId="test-id"/>);
        await waitFor(() => {
            const elt = document.querySelector('.bullet');
            expect(elt).toBeInTheDocument();
        });
    });

    it('processes type and threshold props correctly when type is not linear', async () => {
        render(<Metric type="angular" threshold={50} testId="test-id"/>);
        await waitFor(() => {
            const elt = document.querySelector('.angular');
            expect(elt).toBeInTheDocument();
        });
    });

    it('applies style correctly when height is undefined', async () => {
        render(<Metric testId="test-id"/>);
        await waitFor(() => {
            const elt = document.querySelector('.js-plotly-plot');
            expect(elt).toHaveStyle({
                width: '100%',
                position: 'relative',
                display: 'inline-block'
            });
        });
    });

    it('processes type prop correctly when type is none', async () => {
        render(<Metric type="none" testId="test-id"/>);
        await waitFor(() => {
            const angularElm = document.querySelector('.angular');
            const angularAxis = document.querySelector('.angularaxis');
            expect(angularElm).not.toBeInTheDocument();
            expect(angularAxis).not.toBeInTheDocument();
        });
    });

    it('processes template_Dark_ prop correctly when theme is dark', async () => {
        const darkTheme = createTheme({
            palette: {
                mode: 'dark',
            },
        });

        render(
            <ThemeProvider theme={darkTheme}>
                <Metric template_Dark_={JSON.stringify(darkTemplate)} testId="test-id"/>
            </ThemeProvider>
        );
        await waitFor(() => {
            const elt = document.querySelector('.main-svg');
            expect(elt).toHaveStyle({
                backgroundColor: 'rgb(31, 47, 68)'
            });
        });
    });

    it('processes template_Light_ prop correctly when theme is not dark', async () => {
        const lightTheme = createTheme({
            palette: {
                mode: 'light',
            },
        });

        render(
            <ThemeProvider theme={lightTheme}>
                <Metric template_Light_={JSON.stringify(lightTemplate)} testId="test-id"/>
            </ThemeProvider>
        );
        await waitFor(() => {
            const elt = document.querySelector('.main-svg');
            expect(elt).toHaveStyle({
                backgroundColor: 'rgb(255, 255, 255)'
            });
        });
    });

    it('logs an error when template_Dark_ prop is not a valid JSON string', () => {
        const consoleSpy = jest.spyOn(console, 'info');
        render(<Metric template_Dark_="not a valid JSON string" testId="test-id"/>);
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Error while parsing Metric.template'));
        consoleSpy.mockRestore();
    });

    it('logs an error when template_Light_ prop is not a valid JSON string', () => {
        const consoleSpy = jest.spyOn(console, 'info');
        render(<Metric template_Light_="not a valid JSON string" testId="test-id"/>);
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Error while parsing Metric.template'));
        consoleSpy.mockRestore();
    });

});
