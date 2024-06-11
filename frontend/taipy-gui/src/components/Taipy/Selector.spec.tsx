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
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Selector from "./Selector";
import { LoV } from "./lovUtils";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";
import { stringIcon } from "../../utils/icon";

const lov: LoV = [
    ["id1", "Item 1"],
    ["id2", "Item 2"],
    ["id3", "Item 3"],
    ["id4", "Item 4"],
];
const defLov = '[["id10","Default Item"]]';

const imageItem: [string, stringIcon] = ["ii1", { path: "/img/fred.png", text: "Image" }];

describe("Selector Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Selector lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("SPAN");
    });
    it("uses the class", async () => {
        const { getByText } = render(<Selector lov={lov} className="taipy-selector" />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass(
            "taipy-selector"
        );
    });
    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(<Selector lov={lovWithImage} />);
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });
    it("displays the right info for lov vs defaultLov", async () => {
        const { getByText, queryAllByText } = render(<Selector lov={lov} defaultLov={defLov} />);
        getByText("Item 1");
        expect(queryAllByText("Default Item")).toHaveLength(0);
    });
    it("displays the default LoV", async () => {
        const { getByText } = render(<Selector lov={undefined as unknown as []} defaultLov={defLov} />);
        getByText("Default Item");
    });
    it("shows a selection at start", async () => {
        const { getByText } = render(<Selector defaultValue="id1" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement).toHaveClass("Mui-selected");
    });
    it("shows a selection at start through value", async () => {
        const { getByText } = render(<Selector defaultValue="id1" value="id2" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement).not.toHaveClass("Mui-selected");
        const elt2 = getByText("Item 2");
        expect(elt2.parentElement?.parentElement).toHaveClass("Mui-selected");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<Selector lov={lov} active={false} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).toHaveClass("Mui-disabled"));
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<Selector lov={lov} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<Selector lov={lov} active={true} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Selector lov={lov} updateVarName="varname" updateVars="lov=lov" />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 1");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "varname",
            payload: { value: "id1", relvar: "lov" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    //multiple
    describe("Selector Component with multiple", () => {
        it("displays checkboxes when multiple", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={true} />);
            expect(queryAllByRole("checkbox")).toHaveLength(4);
        });
        it("does not display checkboxes when not multiple", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={false} />);
            expect(queryAllByRole("checkbox")).toHaveLength(0);
        });
        it("selects 2 items", async () => {
            const { queryAllByRole } = render(<Selector lov={lov} multiple={true} value={["id1", "id2"]} />);
            const cks = queryAllByRole("checkbox");
            const ccks = cks.filter((ck) => (ck as HTMLInputElement).checked);
            expect(ccks).toHaveLength(2);
        });
        it("selects the checkbox when the line is selected", async () => {
            const { getByText } = render(<Selector lov={lov} multiple={true} value="id2" />);
            const elt = getByText("Item 2");
            const ck = elt.parentElement?.parentElement?.querySelector('input[type="checkbox"]') as HTMLInputElement;
            expect(ck).toBeDefined();
            expect(ck.checked).toBe(true);
        });
        it("dispatch a well formed message for multiple", async () => {
            const user = userEvent.setup();
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByText } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Selector lov={lov} updateVarName="varname" multiple={true} />
                </TaipyContext.Provider>
            );
            const elt = getByText("Item 1");
            await user.click(elt);
            const elt2 = getByText("Item 2");
            await user.click(elt2);
            const elt3 = getByText("Item 3");
            await user.click(elt3);
            await user.click(elt2);
            expect(dispatch).toHaveBeenLastCalledWith({
                name: "varname",
                payload: { value: ["id1", "id3"] },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        });
    });
    describe("Selector Component with filter", () => {
        //filter
        it("displays an input when filter", async () => {
            const { getByPlaceholderText } = render(<Selector lov={lov} filter={true} />);
            getByPlaceholderText("Search field");
        });
        it("does not display an input when filter is off", async () => {
            const { queryAllByPlaceholderText } = render(<Selector lov={lov} filter={false} />);
            expect(queryAllByPlaceholderText("Search field")).toHaveLength(0);
        });
        it("filters items by name", async () => {
            const { getByPlaceholderText, queryAllByText } = render(<Selector lov={lov} filter={true} />);
            expect(queryAllByText(/Item /)).toHaveLength(4);
            const search = getByPlaceholderText("Search field");
            await userEvent.type(search, "m 3");
            expect(queryAllByText(/Item /)).toHaveLength(1);
            await userEvent.clear(search);
            expect(queryAllByText(/Item /)).toHaveLength(4);
        });
    });
    describe("Selector Component with dropdown", () => {
        //dropdown
        it("displays as an empty control with arrow", async () => {
            const { getByTestId } = render(<Selector lov={lov} dropdown={true} />);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays as a simple input with default value", async () => {
            const { getByText, getByTestId, queryAllByTestId } = render(
                <Selector lov={lov} defaultValue="id1" dropdown={true} />
            );
            getByText("Item 1");
            expect(queryAllByTestId("CancelIcon")).toHaveLength(0);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays a delete icon when multiple", async () => {
            const { getByTestId } = render(<Selector lov={lov} defaultValue="id1" dropdown={true} multiple={true} />);
            getByTestId("CancelIcon");
        });
        it("is disabled", async () => {
            const { getByText } = render(<Selector lov={lov} defaultValue="id1" active={false} dropdown={true} />);
            const elt = getByText("Item 1");
            expect(elt.parentElement).toHaveClass("Mui-disabled");
        });
        it("is enabled by default", async () => {
            const { getByText } = render(<Selector lov={lov} defaultValue="id1" dropdown={true} />);
            const elt = getByText("Item 1");
            expect(elt.parentElement).not.toHaveClass("Mui-disabled");
        });
        it("is enabled by active", async () => {
            const { getByText } = render(<Selector defaultValue="id1" lov={lov} active={true} dropdown={true} />);
            const elt = getByText("Item 1");
            expect(elt.parentElement).not.toHaveClass("Mui-disabled");
        });
        it("opens a dropdown on click", async () => {
            const { getByText, getByRole, queryAllByRole } = render(<Selector lov={lov} dropdown={true} />);
            const butElt = getByRole("combobox");
            expect(butElt).toBeInTheDocument();
            await userEvent.click(butElt);
            getByRole("listbox");
            const elt = getByText("Item 2");
            await userEvent.click(elt);
            expect(queryAllByRole("listbox")).toHaveLength(0);
        });
    });

    describe("Selector Component with dropdown + filter", () => {
        //dropdown
        it("displays as an empty control with arrow", async () => {
            const { getByTestId } = render(<Selector lov={lov} dropdown={true} filter={true} />);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays as a simple input with default value", async () => {
            const { getByRole, getByTestId, queryAllByTestId } = render(
                <Selector lov={lov} defaultValue="id1" dropdown={true} filter={true} />
            );
            expect(getByRole("combobox")).toHaveValue("Item 1");
            expect(queryAllByTestId("CancelIcon")).toHaveLength(0);
            getByTestId("ArrowDropDownIcon");
        });
        it("displays a delete icon when multiple", async () => {
            const { getByTestId } = render(
                <Selector lov={lov} defaultValue="id1" dropdown={true} multiple={true} filter={true} />
            );
            getByTestId("CancelIcon");
        });
        it("is disabled", async () => {
            const { getByRole } = render(
                <Selector lov={lov} defaultValue="id1" active={false} dropdown={true} filter={true} />
            );
            const elt = getByRole("combobox");
            expect(elt.parentElement).toHaveClass("Mui-disabled");
        });
        it("is enabled by default", async () => {
            const { getByRole } = render(<Selector lov={lov} defaultValue="id1" dropdown={true} filter={true} />);
            const elt = getByRole("combobox");
            expect(elt.parentElement).not.toHaveClass("Mui-disabled");
        });
        it("is enabled by active", async () => {
            const { getByRole } = render(
                <Selector defaultValue="id1" lov={lov} active={true} dropdown={true} filter={true} />
            );
            const elt = getByRole("combobox");
            expect(elt.parentElement).not.toHaveClass("Mui-disabled");
        });
        it("opens a dropdown on click", async () => {
            const { getByText, getByRole, queryAllByRole } = render(
                <Selector lov={lov} dropdown={true} filter={true} />
            );
            const butElt = getByRole("combobox");
            expect(butElt).toBeInTheDocument();
            await userEvent.click(butElt);
            getByRole("listbox");
            const elt = getByText("Item 2");
            await userEvent.click(elt);
            expect(queryAllByRole("listbox")).toHaveLength(0);
        });
    });
    describe("Selector Component radio mode", () => {
        //dropdown
        it("displays a list of unselected radios", async () => {
            const { getByText, getByRole } = render(<Selector lov={lov} mode="radio" className="taipy-selector" />);
            getByText("Item 1");
            getByRole("radiogroup");
            expect(document.querySelector("div.taipy-selector-radio-group")).not.toBeNull();
        });
        it("displays a list of radios with one selected", async () => {
            const { getByText } = render(<Selector lov={lov} defaultValue="id1" mode="radio" />);
            const elt = getByText("Item 1");
            expect(elt.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
        });
        it("selects on click", async () => {
            const { getByText, getByRole, queryAllByRole } = render(
                <Selector lov={lov} defaultValue="id1" mode="radio" />
            );
            const elt = getByText("Item 2");
            expect(elt.parentElement?.querySelector("span.Mui-checked")).toBeNull();
            await userEvent.click(elt);
            expect(elt.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
        });
    });

    describe("Selector Component check mode", () => {
        //dropdown
        it("displays a list of unselected checks", async () => {
            const { getByText } = render(<Selector lov={lov} mode="check" className="taipy-selector" />);
            const elt = getByText("Item 1");
            expect(elt.parentElement?.parentElement).toHaveClass("taipy-selector-check-group");
            expect(document.querySelector("span.MuiCheckbox-root")).not.toBeNull();
        });
        it("displays a list of checks with one selected", async () => {
            const { getByText } = render(<Selector lov={lov} defaultValue="id1" mode="check" />);
            const elt = getByText("Item 1");
            expect(elt.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
        });
        it("selects on click", async () => {
            const { getByText, getByRole, queryAllByRole } = render(
                <Selector lov={lov} defaultValue="id1" mode="check" />
            );
            const elt1 = getByText("Item 1");
            expect(elt1.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            const elt2 = getByText("Item 2");
            expect(elt2.parentElement?.querySelector("span.Mui-checked")).toBeNull();
            await userEvent.click(elt2);
            expect(elt1.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            expect(elt2.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            const elt3 = getByText("Item 3");
            expect(elt3.parentElement?.querySelector("span.Mui-checked")).toBeNull();
            await userEvent.click(elt3);
            expect(elt1.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            expect(elt2.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            expect(elt3.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            await userEvent.click(elt1);
            expect(elt1.parentElement?.querySelector("span.Mui-checked")).toBeNull();
            expect(elt2.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
            expect(elt3.parentElement?.querySelector("span.Mui-checked")).not.toBeNull();
        });
    });
});
