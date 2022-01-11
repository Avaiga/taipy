import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import AutoLoadingTable from "./AutoLoadingTable";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { TableValueType } from "./tableUtils";

jest.mock(
    "react-virtualized-auto-sizer",
    () =>
        ({ children }: any) =>
            children({ height: 600, width: 600 })
);

const tableValue = {
    "Infinite--asc": {
        data: [
            {
                Entity: "Austria",
                Day_str: "2020-04-01T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 856,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-02T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 823,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-03T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 829,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-04T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 826,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-05T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 712,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-06T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 824,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-07T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 857,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-08T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 829,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-09T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 820,
            },
            {
                Entity: "Austria",
                Day_str: "2020-04-10T00:00:00.000000Z",
                Code: "AUT",
                "Daily hospital occupancy": 771,
            },
        ],
        rowcount: 14477,
        start: 0,
    },
};
const tableColumns = JSON.stringify({ Entity: { dfid: "Entity" } });

describe("AutoLoadingTable Component", () => {
    it("renders", async () => {
        const { getByText } = render(<AutoLoadingTable data={undefined} columns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const { getByText } = render(
            <AutoLoadingTable data={undefined} columns={tableColumns} className="taipy-table" />
        );
        const elt = getByText("Entity").closest("table");
        expect(elt).toHaveClass("taipy-table");
    });
    it("is disabled", async () => {
        const { getByText } = render(<AutoLoadingTable data={undefined} columns={tableColumns} active={false} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<AutoLoadingTable data={undefined} columns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByText } = render(<AutoLoadingTable data={undefined} columns={tableColumns} active={true} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
    });
    it("dispatch a well formed message on sort", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <AutoLoadingTable data={undefined} columns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elt = getByText("Entity");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity"],
                end: 99,
                id: undefined,
                infinite: true,
                orderby: "",
                pagekey: "Infinite--asc",
                sort: "asc",
                start: 0,
                aggregates: [],
                applies: undefined,
                styles: {}
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("dispatch a well formed message at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <AutoLoadingTable id="table" data={undefined} columns={tableColumns} tp_updatevars="varname=varname" />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { id: "table", names: ["varname"] },
            type: "REQUEST_UPDATE",
        });
    });
    it("displays the received data", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = { ...INITIAL_STATE, data: { table: undefined } };
        const { getAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <AutoLoadingTable
                    id="table"
                    data={state.data.table as undefined}
                    columns={tableColumns}
                    defaultKey="Infinite--asc"
                    pageSize={2}
                    tp_updatevars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        const newState = { ...state, data: { ...state.data, table: tableValue } };
        rerender(
            <TaipyContext.Provider value={{ state: newState, dispatch }}>
                <AutoLoadingTable
                    id="table"
                    data={newState.data.table as TableValueType}
                    defaultKey="Infinite--asc"
                    columns={tableColumns}
                    pageSize={2}
                    tp_updatevars="varname=varname"
                />
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
        const { getAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <AutoLoadingTable data={undefined} columns={tableColumns} pageSize={2} />
            </TaipyContext.Provider>
        );
        rerender(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <AutoLoadingTable
                    selected={selected}
                    data={tableValue as TableValueType}
                    defaultKey="Infinite--asc"
                    columns={tableColumns}
                    pageSize={2}
                />
            </TaipyContext.Provider>
        );
        const elts = getAllByText("Austria");
        elts.forEach((elt: HTMLElement, idx: number) =>
            selected.indexOf(idx) == -1
                ? expect(elt.parentElement).not.toHaveClass("Mui-selected")
                : expect(elt.parentElement).toHaveClass("Mui-selected")
        );
        expect(document.querySelectorAll(".Mui-selected")).toHaveLength(selected.length);
    });
});
