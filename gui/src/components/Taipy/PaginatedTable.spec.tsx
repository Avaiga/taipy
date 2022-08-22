import React from "react";
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import PaginatedTable from "./PaginatedTable";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { TableValueType } from "./tableUtils";

const valueKey = "0-100-Entity,Daily hospital occupancy--asc";
const tableValue = {
    [valueKey]: {
        data: [
            {
                Day_str: "2020-04-01T00:00:00.000000Z",
                "Daily hospital occupancy": 856,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-02T00:00:00.000000Z",
                "Daily hospital occupancy": 823,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-03T00:00:00.000000Z",
                "Daily hospital occupancy": 829,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-04T00:00:00.000000Z",
                "Daily hospital occupancy": 826,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-05T00:00:00.000000Z",
                "Daily hospital occupancy": 712,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-06T00:00:00.000000Z",
                "Daily hospital occupancy": 824,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-07T00:00:00.000000Z",
                "Daily hospital occupancy": 857,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-08T00:00:00.000000Z",
                "Daily hospital occupancy": 829,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-09T00:00:00.000000Z",
                "Daily hospital occupancy": 820,
                Entity: "Austria",
                Code: "AUT",
            },
            {
                Day_str: "2020-04-10T00:00:00.000000Z",
                "Daily hospital occupancy": 771,
                Entity: "Austria",
                Code: "AUT",
            },
        ],
        rowcount: 14477,
        start: 0,
    },
};
const tableColumns = JSON.stringify({
    Entity: { dfid: "Entity" },
    "Daily hospital occupancy": { dfid: "Daily hospital occupancy", type: "int64" },
});

describe("PaginatedTable Component", () => {
    it("renders", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} columns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const { getByText } = render(
            <PaginatedTable data={undefined} columns={tableColumns} className="taipy-table" />
        );
        const elt = getByText("Entity").closest("table");
        expect(elt).toHaveClass("taipy-table");
    });
    it("is disabled", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} columns={tableColumns} active={false} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} columns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} columns={tableColumns} active={true} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
    });
    it("dispatch 2 well formed messages at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable id="table" data={undefined} columns={tableColumns} updateVars="varname=varname" />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { id: "table", names: ["varname"] },
            type: "REQUEST_UPDATE",
        });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity", "Daily hospital occupancy"],
                end: 100,
                id: "table",
                orderby: "",
                pagekey: valueKey,
                handlenan: false,
                sort: "asc",
                start: 0,
                aggregates: [],
                applies: undefined,
                styles: {},
                filters: []
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("dispatch a well formed message on sort", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} columns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elt = getByText("Entity");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity", "Daily hospital occupancy"],
                end: 100,
                id: undefined,
                orderby: "Entity",
                pagekey: "0-100-Entity,Daily hospital occupancy-Entity-asc",
                handlenan: false,
                sort: "asc",
                start: 0,
                aggregates: [],
                applies: undefined,
                styles: {},
                filters: []
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("dispatch a well formed message on page change", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = { ...INITIAL_STATE, data: { table: undefined } };
        const { getByLabelText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable
                    id="table"
                    data={state.data.table as undefined}
                    columns={tableColumns}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const newState = { ...state, data: { ...state.data, table: tableValue } };
        rerender(
            <TaipyContext.Provider value={{ state: newState, dispatch }}>
                <PaginatedTable
                    id="table"
                    data={newState.data.table as TableValueType}
                    columns={tableColumns}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const elt = getByLabelText("Go to next page");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity", "Daily hospital occupancy"],
                end: 200,
                id: "table",
                orderby: "",
                pagekey: "100-200-Entity,Daily hospital occupancy--asc",
                handlenan: false,
                sort: "asc",
                start: 100,
                aggregates: [],
                applies: undefined,
                styles: {},
                filters: []
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("displays the received data", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} columns={tableColumns} />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={tableValue as TableValueType} columns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elts = getAllByText("Austria");
        expect(elts.length).toBeGreaterThan(1);
        expect(elts[0].tagName).toBe("DIV");
    });
    it("selects the rows", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const selected = [2, 4, 6];
        const { findAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} columns={tableColumns} />
            </TaipyContext.Provider>
        );
        rerender(
            <TaipyContext.Provider value={{ state: {...state}, dispatch }}>
                <PaginatedTable selected={selected} data={tableValue as TableValueType} columns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elts = await waitFor(() => findAllByText("Austria"));
        elts.forEach((elt: HTMLElement, idx: number) =>
            selected.indexOf(idx) == -1
                ? expect(elt.parentElement?.parentElement).not.toHaveClass("Mui-selected")
                : expect(elt.parentElement?.parentElement).toHaveClass("Mui-selected")
        );
        expect(document.querySelectorAll(".Mui-selected")).toHaveLength(selected.length);
    });
});
