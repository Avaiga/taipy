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
import { getByTitle, render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import TableFilter from "./TableFilter";
import { ColumnDesc } from "./tableUtils";

const tableColumns = {
    StringCol: { dfid: "StringCol", type: "object", index: 0, format: "", filter: true },
    NumberCol: { dfid: "NumberCol", type: "int", index: 1, format: "", filter: true },
    BoolCol: { dfid: "BoolCol", type: "bool", index: 2, format: "", filter: true },
    DateCol: { dfid: "DateCol", type: "datetime", index: 2, format: "", filter: true },
} as Record<string, ColumnDesc>;
const colsOrder = ["StringCol", "NumberCol", "BoolCol", "DateCol"];

beforeEach(() => {
    // add window.matchMedia
    // this is necessary for the date picker to be rendered in desktop mode.
    // if this is not provided, the mobile mode is rendered, which might lead to unexpected behavior
    Object.defineProperty(window, "matchMedia", {
        writable: true,
        value: (query: string): MediaQueryList => ({
            media: query,
            // this is the media query that @material-ui/pickers uses to determine if a device is a desktop device
            matches: query === "(pointer: fine)",
            onchange: () => {},
            addEventListener: () => {},
            removeEventListener: () => {},
            addListener: () => {},
            removeListener: () => {},
            dispatchEvent: () => false,
        }),
    });
});

afterEach(() => {
    // @ts-ignore
    delete window.matchMedia;
});

describe("Table Filter Component", () => {
    it("renders an icon", async () => {
        const { getByTestId } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        expect(elt.parentElement?.parentElement?.tagName).toBe("BUTTON");
    });
    it("renders popover when clicked", async () => {
        const { getByTestId, getAllByText, getAllByTestId } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        expect(getAllByText("Column")).toHaveLength(2);
        expect(getAllByText("Action")).toHaveLength(2);
        expect(getAllByText("Empty String")).toHaveLength(2);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        expect(getByTestId("CheckIcon").parentElement).toBeDisabled();
        expect(getByTestId("DeleteIcon").parentElement).toBeDisabled();
    });
    it("behaves on string column", async () => {
        const { getByTestId, getAllByTestId, findByRole, getByText } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("StringCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("contains"));
        const validate = getByTestId("CheckIcon").parentElement;
        expect(validate).not.toBeDisabled();
    });
    it("behaves on number column", async () => {
        const { getByTestId, getAllByTestId, findByRole, getByText, getAllByText } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("NumberCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("less equals"));
        const validate = getByTestId("CheckIcon").parentElement;
        expect(validate).toBeDisabled();
        const labels = getAllByText("Number");
        expect(labels).toHaveLength(2);
        const input = labels[0].nextElementSibling?.firstElementChild || labels[0];
        await userEvent.click(input);
        await userEvent.keyboard("10");
        expect(validate).not.toBeDisabled();
    });
    it("behaves on boolean column", async () => {
        const { getByTestId, getAllByTestId, findByRole, getByText, getAllByText } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("BoolCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("equals"));
        const validate = getByTestId("CheckIcon").parentElement;
        expect(validate).toBeDisabled();
        const dddElts = getAllByTestId("ArrowDropDownIcon");
        expect(dddElts).toHaveLength(3);
        await userEvent.click(dddElts[2].parentElement?.firstElementChild || dddElts[0]);
        await findByRole("listbox");
        expect(validate).toBeDisabled();
        await userEvent.click(getByText("True"));
        expect(validate).not.toBeDisabled();
    });
    it("behaves on date column", async () => {
        const { getByTestId, getAllByTestId, findByRole, getByText, getByPlaceholderText } = render(
                <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("DateCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("before equal"));
        const validate = getByTestId("CheckIcon").parentElement;
        expect(validate).toBeDisabled();
        const input = getByPlaceholderText("YYYY/MM/DD");
        await userEvent.click(input);
        await userEvent.type(input, "{ArrowLeft}{ArrowLeft}{ArrowLeft}2020/11/11", {delay: 1});
        expect(validate).not.toBeDisabled();
    });
    it("adds a row on validation", async () => {
        const onValidate = jest.fn();
        const { getByTestId, getAllByTestId, findByRole, getByText } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={onValidate} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("StringCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("contains"));
        const validate = getByTestId("CheckIcon");
        expect(validate.parentElement).not.toBeDisabled();
        await userEvent.click(validate);
        const ddElts = getAllByTestId("ArrowDropDownIcon");
        expect(ddElts).toHaveLength(4);
        getByText("1");
        expect(onValidate).toHaveBeenCalled();
    });
    it("delete a row", async () => {
        const onValidate = jest.fn();
        const { getByTestId, getAllByTestId, findByRole, getByText } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={onValidate} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const dropdownElts = getAllByTestId("ArrowDropDownIcon");
        expect(dropdownElts).toHaveLength(2);
        await userEvent.click(dropdownElts[0].parentElement?.firstElementChild || dropdownElts[0]);
        await findByRole("listbox");
        await userEvent.click(getByText("StringCol"));
        await userEvent.click(dropdownElts[1].parentElement?.firstElementChild || dropdownElts[1]);
        await findByRole("listbox");
        await userEvent.click(getByText("contains"));
        const validate = getByTestId("CheckIcon");
        expect(validate.parentElement).not.toBeDisabled();
        await userEvent.click(validate);
        const ddElts = getAllByTestId("ArrowDropDownIcon");
        expect(ddElts).toHaveLength(4);
        const deletes = getAllByTestId("DeleteIcon");
        expect(deletes).toHaveLength(2);
        expect(deletes[0].parentElement).not.toBeDisabled();
        expect(deletes[1].parentElement).toBeDisabled();
        await userEvent.click(deletes[0]);
        const ddElts2 = getAllByTestId("ArrowDropDownIcon");
        expect(ddElts2).toHaveLength(2);
    });
    it("reset filters", async () => {
        const onValidate = jest.fn();
        const { getAllByTestId, getByTestId } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={onValidate} appliedFilters={[{col: "StringCol", action: "==", value: ""}]} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const deletes = getAllByTestId("DeleteIcon");
        expect(deletes).toHaveLength(2);
        expect(deletes[0].parentElement).not.toBeDisabled();
        expect(deletes[1].parentElement).toBeDisabled();
        await userEvent.click(deletes[0]);
        expect(onValidate).toHaveBeenCalled();
    });
    it("ignores unapplicable filters", async () => {
        const { getAllByTestId, getByTestId } = render(
            <TableFilter columns={tableColumns} colsOrder={colsOrder} onValidate={jest.fn()} appliedFilters={[{col: "unknown col", action: "==", value: ""}]} />
        );
        const elt = getByTestId("FilterListIcon");
        await userEvent.click(elt);
        const ddElts2 = getAllByTestId("ArrowDropDownIcon");
        expect(ddElts2).toHaveLength(2);
    });
});
