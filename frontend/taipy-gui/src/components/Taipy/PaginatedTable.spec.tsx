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

import React, { act } from "react";
import { fireEvent, render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import PaginatedTable from "./PaginatedTable";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { TableValueType } from "./tableUtils";

const valueKey = "0-99-Entity,Daily hospital occupancy--asc";
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
const changedValue = {
    [valueKey]: {
        data: [
            {
                Day_str: "2020-04-01T00:00:00.000000Z",
                "Daily hospital occupancy": 856,
                Entity: "Australia",
                Code: "AUS",
            },
        ],
        rowcount: 1,
        start: 0,
    },
};

const editableValue = {
    "0--1-bool,int,float,Code--asc": {
        data: [
            {
                bool: true,
                int: 856,
                float: 1.5,
                Code: "AUT",
            },
            {
                bool: false,
                int: 823,
                float: 2.5,
                Code: "ZZZ",
            },
        ],
        rowcount: 2,
        start: 0,
    },
};
const editableColumns = JSON.stringify({
    bool: { dfid: "bool", type: "bool", index: 0 },
    int: { dfid: "int", type: "int", index: 1 },
    float: { dfid: "float", type: "float", index: 2 },
    Code: { dfid: "Code", type: "str", index: 3 },
});

const buttonImgValue = {
    "0--1-bool,int,float,Code--asc": {
        data: [
            {
                bool: true,
                int: 856,
                float: 1.5,
                Code: "[Button Label](button action)",
            },
            {
                bool: false,
                int: 823,
                float: 2.5,
                Code: "ZZZ",
            },
            {
                bool: true,
                int: 478,
                float: 3.5,
                Code: "![Taipy!](https://docs.taipy.io/en/latest/assets/images/favicon.png)",
            },
        ],
        rowcount: 2,
        start: 0,
    },
};
const buttonColumns = JSON.stringify({
    bool: { dfid: "bool", type: "bool", index: 0 },
    int: { dfid: "int", type: "int", index: 1 },
    float: { dfid: "float", type: "float", index: 2 },
    Code: { dfid: "Code", type: "str", index: 3 },
});

const styledColumns = JSON.stringify({
    Entity: { dfid: "Entity" },
    "Daily hospital occupancy": {
        dfid: "Daily hospital occupancy",
        type: "int64",
        style: "some style function",
        tooltip: "some tooltip",
    },
});

describe("PaginatedTable Component", () => {
    it("renders", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} defaultColumns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for class", async () => {
        const { getByText } = render(
            <PaginatedTable data={undefined} defaultColumns={tableColumns} className="taipy-table" />
        );
        const elt = getByText("Entity").closest("table");
        expect(elt?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-table", "taipy-table-paginated");
    });
    it("is disabled", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} defaultColumns={tableColumns} active={false} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<PaginatedTable data={undefined} defaultColumns={tableColumns} />);
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByText, getAllByTestId } = render(
            <PaginatedTable data={undefined} defaultColumns={tableColumns} active={true} />
        );
        const elt = getByText("Entity");
        expect(elt.parentElement).not.toHaveClass("Mui-disabled");
        expect(getAllByTestId("ArrowDownwardIcon").length).toBeGreaterThan(0);
    });
    it("Hides sort icons when not active", async () => {
        const { queryByTestId } = render(
            <PaginatedTable data={undefined} defaultColumns={tableColumns} active={false} />
        );
        expect(queryByTestId("ArrowDownwardIcon")).toBeNull();
    });
    it("dispatch 2 well formed messages at first render", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable
                    id="table"
                    data={undefined}
                    defaultColumns={tableColumns}
                    updateVars="varname=varname"
                />
            </TaipyContext.Provider>
        );
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { id: "table", names: ["varname"], refresh: false },
            type: "REQUEST_UPDATE",
        });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity", "Daily hospital occupancy"],
                end: 99,
                id: "table",
                orderby: "",
                pagekey: valueKey,
                handlenan: false,
                sort: "asc",
                start: 0,
                aggregates: [],
                applies: undefined,
                styles: undefined,
                tooltips: undefined,
                filters: [],
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("dispatch a well formed message on sort", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elt = getByText("Entity");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                columns: ["Entity", "Daily hospital occupancy"],
                end: 99,
                id: undefined,
                orderby: "Entity",
                pagekey: "0-99-Entity,Daily hospital occupancy-Entity-asc",
                handlenan: false,
                sort: "asc",
                start: 0,
                aggregates: [],
                applies: undefined,
                styles: undefined,
                tooltips: undefined,
                filters: [],
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
                    defaultColumns={tableColumns}
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
                    defaultColumns={tableColumns}
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
                end: 199,
                id: "table",
                orderby: "",
                pagekey: "100-199-Entity,Daily hospital occupancy--asc",
                handlenan: false,
                sort: "asc",
                start: 100,
                aggregates: [],
                applies: undefined,
                styles: undefined,
                tooltips: undefined,
                filters: [],
            },
            type: "REQUEST_DATA_UPDATE",
        });
    });
    it("displays the received data", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={tableValue as TableValueType} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elts = getAllByText("Austria");
        expect(elts.length).toBeGreaterThan(1);
        expect(elts[0].tagName).toBe("SPAN");
    });
    it("displays the refreshed data", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByText, rerender, queryByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={tableValue as TableValueType} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        expect(getAllByText("Austria").length).toBeGreaterThan(1);

        rerender(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={changedValue as TableValueType} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        expect(queryByText("Austria")).toBeNull();
        expect(getAllByText("Australia").length).toBe(1);
    });
    it("selects the rows", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const selected = [2, 4, 6];
        const { findAllByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable selected={selected} data={tableValue as TableValueType} defaultColumns={tableColumns} />
            </TaipyContext.Provider>
        );
        const elts = await waitFor(() => findAllByText("Austria"));
        elts.forEach((elt: HTMLElement, idx: number) =>
            selected.indexOf(idx) == -1
                ? expect(elt.parentElement?.parentElement?.parentElement?.parentElement).not.toHaveClass("Mui-selected")
                : expect(elt.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("Mui-selected")
        );
        expect(document.querySelectorAll(".Mui-selected")).toHaveLength(selected.length);
    });
    describe("Edit Mode", () => {
        it("displays the data with edit buttons", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getAllByTestId, queryAllByTestId, rerender } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <PaginatedTable
                        data={undefined}
                        defaultColumns={editableColumns}
                        editable={true}
                        onEdit="onEdit"
                        showAll={true}
                    />
                </TaipyContext.Provider>
            );

            rerender(
                <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                    <PaginatedTable
                        data={editableValue as TableValueType}
                        defaultColumns={editableColumns}
                        editable={true}
                        onEdit="onEdit"
                        showAll={true}
                    />
                </TaipyContext.Provider>
            );

            expect(document.querySelectorAll(".MuiSwitch-root")).not.toHaveLength(0);
            expect(getAllByTestId("EditIcon")).not.toHaveLength(0);
            expect(queryAllByTestId("CheckIcon")).toHaveLength(0);
            expect(queryAllByTestId("ClearIcon")).toHaveLength(0);
        });
        it("can edit", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByTestId, queryAllByTestId, getAllByTestId, rerender } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <PaginatedTable
                        data={undefined}
                        defaultColumns={editableColumns}
                        editable={true}
                        onEdit="onEdit"
                        showAll={true}
                    />
                </TaipyContext.Provider>
            );

            rerender(
                <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                    <PaginatedTable
                        data={editableValue as TableValueType}
                        defaultColumns={editableColumns}
                        editable={true}
                        onEdit="onEdit"
                        showAll={true}
                    />
                </TaipyContext.Provider>
            );

            const edits = getAllByTestId("EditIcon");
            await userEvent.click(edits[0]);
            const checkButton = getByTestId("CheckIcon");
            getByTestId("ClearIcon");
            await userEvent.click(checkButton);
            expect(queryAllByTestId("CheckIcon")).toHaveLength(0);
            expect(queryAllByTestId("ClearIcon")).toHaveLength(0);

            await userEvent.click(edits[1]);
            const clearButton = getByTestId("ClearIcon");
            const input = document.querySelector("input");
            expect(input).not.toBeNull();
            if (input) {
                if (input.type == "checkbox") {
                    await userEvent.click(input);
                } else {
                    await userEvent.type(input, "1");
                }
            }
            await userEvent.click(clearButton);
            expect(queryAllByTestId("CheckIcon")).toHaveLength(0);
            expect(queryAllByTestId("ClearIcon")).toHaveLength(0);

            dispatch.mockClear();
            await userEvent.click(edits[2]);
            await userEvent.click(getByTestId("CheckIcon"));
            expect(dispatch).toHaveBeenCalledWith({
                name: "",
                payload: {
                    action: "onEdit",
                    args: [],
                    col: "float",
                    index: 0,
                    user_value: 1.5,
                    value: 1.5,
                },
                type: "SEND_ACTION_ACTION",
            });

            await userEvent.click(edits[3]);
            const input2 = document.querySelector("input");
            expect(input2).not.toBeNull();
            if (input2) {
                if (input2.type == "checkbox") {
                    await userEvent.click(input2);
                    await userEvent.click(getByTestId("ClearIcon"));
                } else {
                    await userEvent.type(input2, "{Esc}");
                }
            }

            dispatch.mockClear();
            await userEvent.click(edits[5]);
            const input3 = document.querySelector("input");
            expect(input3).not.toBeNull();
            if (input3) {
                if (input3.type == "checkbox") {
                    await userEvent.click(input3);
                    await userEvent.click(getByTestId("CheckIcon"));
                } else {
                    await userEvent.type(input3, "{Enter}");
                }
            }
            expect(dispatch).toHaveBeenCalledWith({
                name: "",
                payload: {
                    action: "onEdit",
                    args: [],
                    col: "int",
                    index: 1,
                    user_value: 823,
                    value: 823,
                },
                type: "SEND_ACTION_ACTION",
            });
        });
    });
    it("can add", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTestId } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable
                    data={undefined}
                    defaultColumns={editableColumns}
                    showAll={true}
                    editable={true}
                    onAdd="onAdd"
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const addButton = getByTestId("AddIcon");
        await userEvent.click(addButton);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                action: "onAdd",
                args: [],
                index: 0,
            },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("can delete", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getAllByTestId, getByTestId, queryAllByTestId, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable
                    data={undefined}
                    defaultColumns={editableColumns}
                    showAll={true}
                    editable={true}
                    onDelete="onDelete"
                />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={editableValue as TableValueType}
                    defaultColumns={editableColumns}
                    editable={true}
                    showAll={true}
                    onDelete="onDelete"
                />
            </TaipyContext.Provider>
        );

        let deleteButtons = getAllByTestId("DeleteIcon");
        expect(deleteButtons).not.toHaveLength(0);
        await userEvent.click(deleteButtons[0]);
        const checkButton = getByTestId("CheckIcon");
        getByTestId("ClearIcon");
        await userEvent.click(checkButton);
        expect(queryAllByTestId("CheckIcon")).toHaveLength(0);
        expect(queryAllByTestId("ClearIcon")).toHaveLength(0);

        await userEvent.click(deleteButtons[1]);
        const clearButton = getByTestId("ClearIcon");
        const input = document.querySelector("input");
        expect(input).not.toBeNull();
        input && (await userEvent.type(input, "1"));
        await userEvent.click(clearButton);
        expect(queryAllByTestId("CheckIcon")).toHaveLength(0);
        expect(queryAllByTestId("ClearIcon")).toHaveLength(0);

        await userEvent.click(deleteButtons[2]);
        const input3 = document.querySelector("input");
        expect(input3).not.toBeNull();
        input3 && (await userEvent.type(input3, "{esc}"));

        deleteButtons = getAllByTestId("DeleteIcon");

        dispatch.mockClear();
        await userEvent.click(deleteButtons[0]);
        const input2 = document.querySelector("input");
        expect(input2).not.toBeNull();
        input2 && (await userEvent.type(input2, "{enter}"));
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                action: "onDelete",
                args: [],
                index: 0,
            },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("can select", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={editableColumns} showAll={true} onAction="onSelect" />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={editableValue as TableValueType}
                    defaultColumns={editableColumns}
                    showAll={true}
                    onAction="onSelect"
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const elt = getByText("823");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                action: "onSelect",
                args: [],
                col: "int",
                index: 1,
                reason: "click",
                value: undefined,
            },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("can click on button", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={editableColumns} showAll={true} onAction="onSelect" />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={buttonImgValue as TableValueType}
                    defaultColumns={buttonColumns}
                    showAll={true}
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const elt = getByText("Button Label");
        expect(elt.tagName).toBe("BUTTON");
        expect(elt).toBeDisabled();

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={buttonImgValue as TableValueType}
                    defaultColumns={buttonColumns}
                    showAll={true}
                    onAction="onSelect"
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const elt2 = getByText("Button Label");
        expect(elt2.tagName).toBe("BUTTON");
        await userEvent.click(elt2);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                action: "onSelect",
                args: [],
                col: "Code",
                index: 0,
                reason: "button",
                value: "button action",
            },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("can show an image", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByAltText, rerender } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <PaginatedTable data={undefined} defaultColumns={editableColumns} showAll={true} onAction="onSelect" />
            </TaipyContext.Provider>
        );

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={buttonImgValue as TableValueType}
                    defaultColumns={buttonColumns}
                    showAll={true}
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const elt = getByAltText("Taipy!");
        expect(elt.tagName).toBe("IMG");

        rerender(
            <TaipyContext.Provider value={{ state: { ...state }, dispatch }}>
                <PaginatedTable
                    data={buttonImgValue as TableValueType}
                    defaultColumns={buttonColumns}
                    showAll={true}
                    onAction="onSelect"
                />
            </TaipyContext.Provider>
        );

        dispatch.mockClear();
        const elt2 = getByAltText("Taipy!");
        expect(elt2.tagName).toBe("IMG");
        await userEvent.click(elt2);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: {
                action: "onSelect",
                args: [],
                col: "Code",
                index: 2,
                reason: "button",
                value: "Taipy!",
            },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("should render correctly when style is applied to columns", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        await waitFor(() => {
            render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <PaginatedTable
                        data={tableValue}
                        defaultColumns={styledColumns}
                        lineStyle={"class_name=rows-bordered"}
                    />
                </TaipyContext.Provider>
            );
        });
        const elt = document.querySelector('table[aria-labelledby="tableTitle"]');
        expect(elt).toBeInTheDocument();
    });
    it("should sort the table in ascending order", async () => {
        await waitFor(() => {
            render(<PaginatedTable data={tableValue} defaultColumns={tableColumns} />);
        });
        const elt = document.querySelector('svg[data-testid="ArrowDownwardIcon"]');
        act(() => {
            fireEvent.click(elt as Element);
        });
        expect(document.querySelector('th[aria-sort="ascending"]')).toBeInTheDocument();
    });
    it("should handle rows per page change", async () => {
        const { getByRole, queryByRole } = render(<PaginatedTable data={tableValue} defaultColumns={tableColumns} />);
        const rowsPerPageDropdown = getByRole("combobox");
        fireEvent.mouseDown(rowsPerPageDropdown);
        const option = queryByRole("option", { selected: false, name: "50" });
        fireEvent.click(option as Element);
        const table = document.querySelector(
            'table[aria-labelledby="tableTitle"].MuiTable-root.MuiTable-stickyHeader'
        );
        expect(table).toBeInTheDocument();
    });
    it("should allow all rows", async () => {
        const { getByRole, queryByRole } = render(
            <PaginatedTable data={tableValue} defaultColumns={tableColumns} allowAllRows={true} />
        );
        const rowsPerPageDropdown = getByRole("combobox");
        fireEvent.mouseDown(rowsPerPageDropdown);
        const option = queryByRole("option", { selected: false, name: "All" });
        expect(option).toBeInTheDocument();
    });
    it("should display row per page correctly", async () => {
        const { getByRole, queryByRole } = render(
            <PaginatedTable
                data={tableValue}
                defaultColumns={tableColumns}
                pageSizeOptions={JSON.stringify([10, 20, 30])}
            />
        );
        const rowsPerPageDropdown = getByRole("combobox");
        fireEvent.mouseDown(rowsPerPageDropdown);
        const option = queryByRole("option", { selected: false, name: "10" });
        expect(option).toBeInTheDocument();
    });
    it("logs error when pageSizeOptions prop is invalid", () => {
        // Create a spy on console.log
        const logSpy = jest.spyOn(console, "log");
        // Render the component with invalid pageSizeOptions prop
        render(<PaginatedTable data={tableValue} defaultColumns={tableColumns} pageSizeOptions={"not a valid json"} />);
        // Check if console.log was called with the expected arguments
        expect(logSpy).toHaveBeenCalledWith(
            "PaginatedTable pageSizeOptions is wrong ",
            "not a valid json",
            expect.any(Error)
        );
        // Clean up the spy
        logSpy.mockRestore();
    });
});
