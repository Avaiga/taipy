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

import React from "react";
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Chart, { TraceValueType } from "./Chart";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

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
            "2020-04-10T00:00:00.000000Z",
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
            "Austria",
        ],
        "Daily hospital occupancy": [856, 823, 829, 826, 712, 824, 857, 829, 820, 771],
    },
};
const chartConfig = JSON.stringify({
    columns: { Day_str: { dfid: "Day" }, "Daily hospital occupancy": { dfid: "Daily hospital occupancy" } },
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
            17.6398, 48.5765, 48.4407, 48.2286,
        ],
        Lon: [
            -112.8352, -65.804, -113.4784, -114.0702, -111.0188, -110.7939, -109.4629, -114.9123, -112.9705, -113.965,
            -66.5401, -111.5245, -64.7246, -112.1932, -113.3159, -104.5863,
        ],
        Globvalue: [
            0.0875, 0.0892, 0.0908, 0.0933, 0.0942, 0.095, 0.095, 0.095, 0.0958, 0.0958, 0.0958, 0.0958, 0.0958, 0.0975,
            0.0983, 0.0992,
        ],
    },
};
const mapConfig = JSON.stringify({
    columns: { Lat: { dfid: "Lat" }, Lon: { dfid: "Lon" } },
    traces: [["Lat", "Lon"]],
    xaxis: ["x"],
    yaxis: ["y"],
    types: ["scattermapbox"],
    modes: ["markers"],
    axisNames: [["lon", "lat"]]
});

const mapLayout = JSON.stringify({
    dragmode: "zoom",
    mapbox: { style: "open-street-map", center: { lat: 38, lon: -90 }, zoom: 3 },
    margin: { r: 0, t: 0, b: 0, l: 0 }
})

describe("Chart Component", () => {
    it("renders", async () => {
        const { getByTestId } = render(<Chart data={chartValue} defaultConfig={chartConfig} testId="test" />);
        const elt = getByTestId("test");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const { getByTestId } = render(
            <Chart data={chartValue} defaultConfig={chartConfig} testId="test" className="taipy-chart" />
        );
        const elt = getByTestId("test");
        expect(elt).toHaveClass("taipy-chart");
    });
    it("is disabled", async () => {
        const { getByTestId } = render(<Chart data={chartValue} defaultConfig={chartConfig} testId="test" active={false} />);
        const elt = getByTestId("test");
        expect(elt.querySelector(".modebar")).toBeNull();
    });
    it("is enabled by default", async () => {
        const { getByTestId } = render(<Chart data={undefined} defaultConfig={chartConfig} testId="test" />);
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
    });
    it("is enabled by active", async () => {
        const { getByTestId } = render(<Chart data={undefined} defaultConfig={chartConfig} testId="test" active={true} />);
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
    });
    it("dispatch 2 well formed messages at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const selProps = { selected0: JSON.stringify([2, 4, 6]) };
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart id="chart" data={undefined} updateVarName="data_var" defaultConfig={chartConfig} updateVars="varname=varname" {...selProps} />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { id: "chart", names: ["varname"], refresh: false },
            type: "REQUEST_UPDATE",
        });
        expect(dispatch).toHaveBeenCalledWith({
            name: "data_var",
            payload: {
                alldata: true,
                pagekey: "Day-Daily hospital occupancy",
                columns: ["Day", "Daily hospital occupancy"],
                decimatorPayload: undefined,
                id: "chart",
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("dispatch a well formed message on selection", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTestId } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart data={undefined} updateVarName="data_var" defaultConfig={chartConfig} testId="test" />
            </TaipyContext.Provider>
        );
        const elt = getByTestId("test");
        await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
        const modebar = elt.querySelector(".modebar");
        modebar && await userEvent.click(modebar);
        expect(dispatch).toHaveBeenCalledWith({
            name: "data_var",
            payload: {
                alldata: true,
                columns: ["Day","Daily hospital occupancy"],
                decimatorPayload: undefined,
                pagekey: "Day-Daily hospital occupancy",
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    xit("dispatch a well formed message on relayout", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = { ...INITIAL_STATE, data: { table: undefined } };
        const { getByLabelText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart
                    id="table"
                    updateVarName="data_var"
                    data={state.data.table as undefined}
                    defaultConfig={chartConfig}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const newState = { ...state, data: { ...state.data, table: chartValue } };
        rerender(
            <TaipyContext.Provider value={{ state: newState, dispatch }}>
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
                start: 100,
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    xit("displays the received data", async () => {
        const { getAllByText, rerender } = render(
            <Chart data={undefined} defaultConfig={chartConfig} updateVars="varname=varname" />
        );
        rerender(<Chart data={chartValue} defaultConfig={chartConfig} updateVars="varname=varname" />);
        const elts = getAllByText("Austria");
        expect(elts.length).toBeGreaterThan(1);
        expect(elts[0].tagName).toBe("TD");
    });
    describe("Chart Component as Map", () => {
        it("renders", async () => {
            const { getByTestId } = render(<Chart data={mapValue} defaultConfig={mapConfig} layout={mapLayout} testId="test" />);
            const elt = getByTestId("test");
            await waitFor(() => expect(elt.querySelector(".modebar")).not.toBeNull());
        });
    });
});
