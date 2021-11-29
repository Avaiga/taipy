import React from "react";
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import { PlotMouseEvent } from "plotly.js";

import Chart, { TraceValueType } from "./Chart";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

const chartValue = {
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
};
const chartConfig = JSON.stringify({
    columns: { Day_str: { dfid: "Day" }, "Daily hospital occupancy": { dfid: "Daily hospital occupancy" } },
    traces: [["Day_str", "Daily hospital occupancy"]],
    xaxis: ["x"],
    yaxis: ["y"],
    types: ["scatter"],
    modes: ["lines+markers"]
});

describe("Chart Component", () => {
    it("renders", async () => {
        const { getByTestId } = render(<Chart value={chartValue} config={chartConfig} testId="test" />);
        const elt = getByTestId("test");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const { getByTestId } = render(<Chart value={chartValue} config={chartConfig} testId="test" className="taipy-chart" />);
        const elt = getByTestId("test");
        expect(elt).toHaveClass("taipy-chart");
    });
    xit("is disabled", async () => {
        const { getByTestId } = render(<Chart value={chartValue} config={chartConfig} testId="test" active={false} />);
        const elt = getByTestId("test ");
        expect(elt).toHaveClass("Mui-disabled");
    });
    xit("is enabled by default", async () => {
        const { getByText } = render(<Chart value={undefined} config={chartConfig} />);
        const elt = getByText("Entity");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    xit("is enabled by active", async () => {
        const { getByText } = render(<Chart value={undefined} config={chartConfig} active={true} />);
        const elt = getByText("Entity");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("dispatch 2 well formed messages at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const selProps = {"selected0": JSON.stringify([2, 4, 6])}
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart id="chart" value={undefined} config={chartConfig} tp_updatevars="varname=varname" {...selProps} />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { id: "chart", names: ["varname"] },
            type: "REQUEST_UPDATE",
        });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                alldata: true,
                columns: ["Day", "Daily hospital occupancy"],
                id: "chart"
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    xit("dispatch a well formed message on selection", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTestId } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart value={undefined} config={chartConfig} testId="test" />
            </TaipyContext.Provider>
        );
        const elt = getByTestId("test");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity"],
                end: 100,
                id: undefined,
                orderby: "Entity",
                pagekey: "0-100-Entity-asc",
                sort: "asc",
                start: 0,
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    xit("dispatch a well formed message on relayout", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = { ...INITIAL_STATE, data: { table: undefined } };
        const { getByLabelText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Chart id="table" value={state.data.table as undefined} config={chartConfig} tp_updatevars="varname=varname" />
            </TaipyContext.Provider>
        );
        const newState = { ...state, data: { ...state.data, table: chartValue } };
        rerender(
            <TaipyContext.Provider value={{ state: newState, dispatch }}>
                <Chart id="table" value={newState.data.table as TraceValueType} config={chartConfig} tp_updatevars="varname=varname" />
            </TaipyContext.Provider>
        );
        const elt = getByLabelText("Go to next page");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
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
            <Chart value={undefined} config={chartConfig} tp_updatevars="varname=varname" />
        );
        rerender(
            <Chart value={chartValue} config={chartConfig} tp_updatevars="varname=varname" />
        );
        const elts = getAllByText("Austria");
        expect(elts.length).toBeGreaterThan(1);
        expect(elts[0].tagName).toBe("TD");
    });
});
