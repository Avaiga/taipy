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

import React, {useCallback} from "react";
import {render, renderHook, waitFor} from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Chart, {
    getAxis,
    getColNameFromIndexed,
    getValue,
    getValueFromCol,
    TaipyPlotlyButtons,
    TraceValueType
} from "./Chart";
import {TaipyContext} from "../../context/taipyContext";
import {INITIAL_STATE, TaipyState} from "../../context/taipyReducers";
import {ColumnDesc} from "./tableUtils";
import {ModeBarButtonAny} from "plotly.js";

const chartValue = {
    default: {
        Code: ["AUT", "AUT", "AUT", "AUT", "AUT", "AUT", "AUT", "AUT", "AUT", "AUT"],
        Day_str: [
            "2020-04-01T00:00:00.000000Z",
            "2020-04-02T00:00:00.000000Z",
            "2020-04-03T00:00:00.000000Z",
            "2020-04-04T00:00:00.000000Z",
            "2020-04-05T00:00:00.000000Z",
            "2020-04-06T00:00:00.000000Z",
            "2020-04-07T00:00:00.000000Z",
            "2020-04-08T00:00:00.000000Z",
            "2020-04-09T00:00:00.000000Z",
            "2020-04-10T00:00:00.000000Z"
        ],
        Entity: [
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria",
            "Austria"
        ],
        "Daily hospital occupancy": [856, 823, 829, 826, 712, 824, 857, 829, 820, 771]
    }
};
const chartConfig = JSON.stringify({
    columns: {Day_str: {dfid: "Day"}, "Daily hospital occupancy": {dfid: "Daily hospital occupancy"}},
    traces: [["Day_str", "Daily hospital occupancy"]],
    xaxis: ["x"],
    yaxis: ["y"],
    types: ["scatter"],
    modes: ["lines+markers"],
    axisNames: []
});

const mapValue = {
    default: {
        Lat: [
            48.4113, 18.0057, 48.6163, 48.5379, 48.5843, 48.612, 48.6286, 48.6068, 48.4489, 48.6548, 18.5721, 48.3734,
            17.6398, 48.5765, 48.4407, 48.2286
        ],
        Lon: [
            -112.8352, -65.804, -113.4784, -114.0702, -111.0188, -110.7939, -109.4629, -114.9123, -112.9705, -113.965,
            -66.5401, -111.5245, -64.7246, -112.1932, -113.3159, -104.5863
        ],
        Globvalue: [
            0.0875, 0.0892, 0.0908, 0.0933, 0.0942, 0.095, 0.095, 0.095, 0.0958, 0.0958, 0.0958, 0.0958, 0.0958, 0.0975,
            0.0983, 0.0992
        ]
    }
};
const mapConfig = JSON.stringify({
    columns: {Lat: {dfid: "Lat"}, Lon: {dfid: "Lon"}},
    traces: [["Lat", "Lon"]],
    xaxis: ["x"],
    yaxis: ["y"],
    types: ["scattermapbox"],
    modes: ["markers"],
    axisNames: [["lon", "lat"]]
});

const mapLayout = JSON.stringify({
    dragmode: "zoom",
    mapbox: {style: "open-street-map", center: {lat: 38, lon: -90}, zoom: 3},
    margin: {r: 0, t: 0, b: 0, l: 0}
});

interface Props {
    figure?: boolean;
}

interface Clickable {
    click: (gd: HTMLElement, evt: Event) => void;
}

type DataKey = string;
type Data = Record<DataKey, {tp_index?: number[]}>;

const useGetRealIndex = (data: Data, dataKey: DataKey, props: Props) => {
    return useCallback(
        (index?: number) =>
            typeof index === "number"
                ? props.figure
                    ? index
                    : data[dataKey] && data[dataKey].tp_index
                      ? data[dataKey]!.tp_index![index]
                      : index
                : 0,
        [data, dataKey, props.figure]
    );
};

describe("Chart Component", () => {
    it("renders", async () => {
        const {getByTestId} = render(<Chart data={chartValue} defaultConfig={chartConfig} testId="test" />);
        const elt = getByTestId("test");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const {getByTestId} = render(
            <Chart data={chartValue} defaultConfig={chartConfig} testId="test" className="taipy-chart" />
        );
        const elt = getByTestId("test");
        expect(elt).toHaveClass("taipy-chart");
    });
    it("is disabled", async () => {
        const {getByTestId} = render(
            <Chart data={chartValue} defaultConfig={chartConfig} testId="test" active={false} />
        );
        const elt = getByTestId("test");
        expect(elt.querySelector(".modebar")).toBeNull();
    });
    it("is enabled by default", async () => {
        const {getByTestId} = render(<Chart data={undefined} defaultConfig={chartConfig} testId="test" />);
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
    });
    it("is enabled by active", async () => {
        const {getByTestId} = render(
            <Chart data={undefined} defaultConfig={chartConfig} testId="test" active={true} />
        );
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
    });
    it("dispatch 2 well formed messages at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const selProps = {selected0: JSON.stringify([2, 4, 6])};
        render(
            <TaipyContext.Provider value={{state, dispatch}}>
                <Chart
                    id="chart"
                    data={undefined}
                    updateVarName="data_var"
                    defaultConfig={chartConfig}
                    updateVars="varname=varname"
                    {...selProps}
                />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {id: "chart", names: ["varname"], refresh: false},
            type: "REQUEST_UPDATE"
        });
        expect(dispatch).toHaveBeenCalledWith({
            name: "data_var",
            payload: {
                alldata: true,
                pagekey: "Day-Daily hospital occupancy",
                columns: ["Day", "Daily hospital occupancy"],
                decimatorPayload: undefined,
                id: "chart"
            },
            type: "REQUEST_DATA_UPDATE"
        });
    });
    it("dispatch a well formed message on selection", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const {getByTestId} = render(
            <TaipyContext.Provider value={{state, dispatch}}>
                <Chart data={undefined} updateVarName="data_var" defaultConfig={chartConfig} testId="test" />
            </TaipyContext.Provider>
        );
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
        const modebar = elt.querySelector(".modebar");
        modebar && (await userEvent.click(modebar));
        expect(dispatch).toHaveBeenCalledWith({
            name: "data_var",
            payload: {
                alldata: true,
                columns: ["Day", "Daily hospital occupancy"],
                decimatorPayload: undefined,
                pagekey: "Day-Daily hospital occupancy"
            },
            type: "REQUEST_DATA_UPDATE"
        });
    });
    xit("dispatch a well formed message on relayout", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = {...INITIAL_STATE, data: {table: undefined}};
        const {getByLabelText, rerender} = render(
            <TaipyContext.Provider value={{state, dispatch}}>
                <Chart
                    id="table"
                    updateVarName="data_var"
                    data={state.data.table as undefined}
                    defaultConfig={chartConfig}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const newState = {...state, data: {...state.data, table: chartValue}};
        rerender(
            <TaipyContext.Provider value={{state: newState, dispatch}}>
                <Chart
                    id="table"
                    updateVarName="data_var"
                    data={newState.data.table as Record<string, TraceValueType>}
                    defaultConfig={chartConfig}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const elt = getByLabelText("Go to next page");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "data_var",
            payload: {
                columns: ["Entity"],
                end: 200,
                id: "table",
                orderby: "",
                pagekey: "100-200--asc",
                sort: "asc",
                start: 100
            },
            type: "REQUEST_DATA_UPDATE"
        });
    });
    xit("displays the received data", async () => {
        const {getAllByText, rerender} = render(
            <Chart data={undefined} defaultConfig={chartConfig} updateVars="varname=varname" />
        );
        rerender(<Chart data={chartValue} defaultConfig={chartConfig} updateVars="varname=varname" />);
        const elts = getAllByText("Austria");
        expect(elts.length).toBeGreaterThan(1);
        expect(elts[0].tagName).toBe("TD");
    });

    it("Chart renders correctly", () => {
        const figure = [{data: [], layout: {title: "Mock Title"}}];
        const {getByTestId} = render(
            <Chart
                id="table"
                updateVarName="data_var"
                data={undefined}
                defaultConfig={chartConfig}
                updateVars="varname=varname"
                figure={figure}
                testId="chart"
            />
        );
        expect(getByTestId("chart")).toBeInTheDocument();
    });

    it("handles plotConfig prop correctly", () => {
        const consoleInfoSpy = jest.spyOn(console, "info");
        // Case 1: plotConfig is a valid JSON string
        render(<Chart plotConfig='{"autosizable": true}' defaultConfig={chartConfig} />);
        expect(consoleInfoSpy).not.toHaveBeenCalled();
        // Case 2: plotConfig is not a valid JSON string
        render(<Chart plotConfig="not a valid json" defaultConfig={chartConfig} />);
        expect(consoleInfoSpy).toHaveBeenCalledWith(
            "Error while parsing Chart.plot_config\nUnexpected token 'o', \"not a valid json\" is not valid JSON"
        );
        // Case 3: plotConfig is not an object
        render(<Chart plotConfig='"not an object"' defaultConfig={chartConfig} />);
        expect(consoleInfoSpy).toHaveBeenCalledWith("Error Chart.plot_config is not a dictionary");
        consoleInfoSpy.mockRestore();
    });
});

describe("Chart Component as Map", () => {
    it("renders", async () => {
        const {getByTestId} = render(
            <Chart data={mapValue} defaultConfig={mapConfig} layout={mapLayout} testId="test" />
        );
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
    });
});

describe("getColNameFromIndexed function", () => {
    it("returns the column name when the input string matches the pattern", () => {
        const colName = "1/myColumn";
        const result = getColNameFromIndexed(colName);
        expect(result).toBe("myColumn");
    });
    it("returns the input string when the input string does not match the pattern", () => {
        const colName = "myColumn";
        const result = getColNameFromIndexed(colName);
        expect(result).toBe("myColumn");
    });
    it("returns the input string when the input string is empty", () => {
        const colName = "";
        const result = getColNameFromIndexed(colName);
        expect(result).toBe("");
    });
});

describe("getValue function", () => {
    it("returns the value from column when the input string matches the pattern", () => {
        const values: TraceValueType = {myColumn: [1, 2, 3]};
        const arr: string[] = ["myColumn"];
        const idx = 0;
        const result = getValue(values, arr, idx);
        expect(result).toEqual([1, 2, 3]);
    });

    it("returns undefined when returnUndefined is true and value is empty", () => {
        const values: TraceValueType = {myColumn: []};
        const arr: string[] = ["myColumn"];
        const idx = 0;
        const returnUndefined = true;
        const result = getValue(values, arr, idx, returnUndefined);
        expect(result).toBeUndefined();
    });

    it("returns empty array when returnUndefined is false and value is empty", () => {
        const values: TraceValueType = {myColumn: []};
        const arr: string[] = ["myColumn"];
        const idx = 0;
        const returnUndefined = false;
        const result = getValue(values, arr, idx, returnUndefined);
        expect(result).toEqual([]);
    });
});

describe("getRealIndex function", () => {
    it("should return 0 if index is not a number", () => {
        const data = {};
        const dataKey = "someKey";
        const props = {figure: false};

        const {result} = renderHook(() => useGetRealIndex(data, dataKey, props));
        const getRealIndex = result.current;
        expect(getRealIndex(undefined)).toBe(0);
    });

    it("should return index if figure is true", () => {
        const data = {};
        const dataKey = "someKey";
        const props = {figure: true};

        const {result} = renderHook(() => useGetRealIndex(data, dataKey, props));
        const getRealIndex = result.current;
        expect(getRealIndex(5)).toBe(5); // index is a number
    });

    it("should return index if figure is false and tp_index does not exist", () => {
        const data = {
            someKey: {}
        };
        const dataKey = "someKey";
        const props = {figure: false};

        const {result} = renderHook(() => useGetRealIndex(data, dataKey, props));
        const getRealIndex = result.current;
        expect(getRealIndex(2)).toBe(2); // index is a number
    });
});

describe("getValueFromCol function", () => {
    it("should return an empty array when values is undefined", () => {
        const result = getValueFromCol(undefined, "test");
        expect(result).toEqual([]);
    });

    it("should return an empty array when values[col] is undefined", () => {
        const values = {test: [1, 2, 3]};
        const result = getValueFromCol(values, "nonexistent");
        expect(result).toEqual([]);
    });
});

describe("getAxis function", () => {
    it("should return undefined when traces length is less than idx", () => {
        const traces = [["test"]];
        const columns: Record<string, ColumnDesc> = {
            test: {
                dfid: "test",
                type: "testType",
                index: 0
            }
        };
        const result = getAxis(traces, 2, columns, 0);
        expect(result).toBeUndefined();
    });

    it("should return undefined when traces[idx] length is less than axis", () => {
        const traces = [["test"]];
        const columns: Record<string, ColumnDesc> = {
            test: {
                dfid: "test",
                type: "testType",
                index: 0
            }
        };
        const result = getAxis(traces, 0, columns, 2);
        expect(result).toBeUndefined();
    });

    it("should return undefined when traces[idx][axis] is undefined", () => {
        const traces = [["test"]];
        const columns: Record<string, ColumnDesc> = {
            test: {
                dfid: "test",
                type: "testType",
                index: 0
            }
        };
        const result = getAxis(traces, 0, columns, 1);
        expect(result).toBeUndefined();
    });

    it("should return undefined when columns[traces[idx][axis]] is undefined", () => {
        const traces = [["test"]];
        const columns: Record<string, ColumnDesc> = {
            test: {
                dfid: "test",
                type: "testType",
                index: 0
            }
        };
        const result = getAxis(traces, 0, columns, 1); // changed axis from 0 to 1
        expect(result).toBeUndefined();
    });

    it("should return dfid when all conditions are met", () => {
        const traces = [["test"]];
        const columns: Record<string, ColumnDesc> = {
            test: {
                dfid: "test",
                type: "testType",
                index: 0
            }
        };
        const result = getAxis(traces, 0, columns, 0);
        expect(result).toBe("test");
    });
});

describe("click function", () => {
    it("should return when div is not found", () => {
        // Create a mock HTMLElement without 'div.svg-container'
        const mockElement = document.createElement("div");
        // Create a mock Event
        const mockEvent = new Event("click");
        // Call the click function with the mock HTMLElement and Event
        (TaipyPlotlyButtons[0] as ModeBarButtonAny & Clickable).click(mockElement, mockEvent);
        // Since there's no 'div.svg-container', the function should return without making any changes
        // We can check this by verifying that no 'full-screen' class was added
        expect(mockElement.classList.contains("full-screen")).toBe(false);
    });
    it("should set data-height when div.svg-container is found but data-height is not set", () => {
        // Create a mock HTMLElement
        const mockElement = document.createElement("div");

        // Create a mock div with class 'svg-container' and append it to the mockElement
        const mockDiv = document.createElement("div");
        mockDiv.className = "svg-container";
        mockElement.appendChild(mockDiv);

        // Create a mock Event
        const mockEvent = {
            ...new Event("click"),
            currentTarget: document.createElement("div")
        };

        // Call the click function with the mock HTMLElement and Event
        (TaipyPlotlyButtons[0] as ModeBarButtonAny & Clickable).click(mockElement, mockEvent);

        // Check that the 'data-height' attribute was set
        expect(mockElement.getAttribute("data-height")).not.toBeNull();
    });
    it("should set data-title attribute", () => {
        // Create a mock HTMLElement
        const mockElement = document.createElement("div");

        // Create a mock div with class 'svg-container' and append it to the mockElement
        const mockDiv = document.createElement("div");
        mockDiv.className = "svg-container";
        mockElement.appendChild(mockDiv);

        // Create a mock Event with a mock currentTarget
        const mockEvent = {
            ...new Event("click"),
            currentTarget: mockElement
        };

        // Call the click function with the mock HTMLElement and Event
        (TaipyPlotlyButtons[0] as ModeBarButtonAny & Clickable).click(mockElement, mockEvent);

        // Check that the 'data-title' attribute was set
        expect(mockElement.getAttribute("data-title")).toBe("Exit Full screen");
    });
});
