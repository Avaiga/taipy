/*
 * Copyright 2023 Avaiga Private Limited
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

import TreeView from "./TreeView";
import { LoV } from "./lovUtils";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";
import { stringIcon } from "../../utils/icon";

const lov: LoV = [
    [
        "id1",
        "Item 1",
        [
            ["id1.1", "Item 1.1"],
            ["id1.2", "Item 1.2"],
        ],
    ],
    ["id2", "Item 2"],
    ["id3", "Item 3"],
    ["id4", "Item 4"],
];
const defLov = '[["id10","Default Item"]]';

const imageItem: [string, stringIcon] = ["ii1", { path: "/img/fred.png", text: "Image" }];

describe("TreeView Component", () => {
    it("renders", async () => {
        const { getByText } = render(<TreeView lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("DIV");
    });
    it("uses the class", async () => {
        const { getByText } = render(<TreeView lov={lov} className="taipy-tree" />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-tree");
    });
    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(<TreeView lov={lovWithImage} />);
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });
    it("shows a tree", async () => {
        const { getByText, queryAllByText } = render(<TreeView lov={lov} filter={true} />);
        const elt = getByText("Item 1");
        expect(queryAllByText(/Item 1\./)).toHaveLength(0);
        const icon = elt.parentElement?.querySelector(".MuiTreeItem-iconContainer") || elt;
        expect(icon).toBeInTheDocument();
        await userEvent.click(icon);
        getByText("Item 1.2");
        expect(queryAllByText(/Item 1\./)).toHaveLength(2);
    });
    it("displays the right info for lov vs defaultLov", async () => {
        const { getByText, queryAllByText } = render(<TreeView lov={lov} defaultLov={defLov} />);
        getByText("Item 1");
        expect(queryAllByText("Default Item")).toHaveLength(0);
    });
    it("displays the default LoV", async () => {
        const { getByText } = render(<TreeView lov={undefined as unknown as []} defaultLov={defLov} />);
        getByText("Default Item");
    });
    it("shows a selection at start", async () => {
        const { getByText } = render(<TreeView defaultValue="id1" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement).toHaveClass("Mui-selected");
    });
    it("shows a selection at start through value", async () => {
        const { getByText } = render(<TreeView defaultValue="id1" value="id2" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement).not.toHaveClass("Mui-selected");
        const elt2 = getByText("Item 2");
        expect(elt2.parentElement).toHaveClass("Mui-selected");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<TreeView lov={lov} active={false} />);
        const elts = getAllByRole("treeitem");
        elts.forEach((elt) => expect(elt.firstElementChild).toHaveClass("Mui-disabled"));
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<TreeView lov={lov} />);
        const elts = getAllByRole("treeitem");
        elts.forEach((elt) => expect(elt.firstElementChild).not.toHaveClass("Mui-disabled"));
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<TreeView lov={lov} active={true} />);
        const elts = getAllByRole("treeitem");
        elts.forEach((elt) => expect(elt.firstElementChild).not.toHaveClass("Mui-disabled"));
    });
    it("dispatch a well formed message base", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <TreeView lov={lov} updateVarName="varname" />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 1");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "varname",
            payload: { value: ["id1"] },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    //multiple
    it("selects 2 items", async () => {
        const { queryAllByRole } = render(<TreeView lov={lov} multiple={true} value={["id1", "id2"]} />);
        expect(document.querySelectorAll(".Mui-selected")).toHaveLength(2);
    });
    it("dispatch a well formed message for multiple", async () => {
        const user = userEvent.setup()
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <TreeView lov={lov} updateVarName="varname" multiple={true} />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 1");
        await user.click(elt);
        const elt2 = getByText("Item 2");
        const elt3 = getByText("Item 3");
        await user.keyboard('{Control>}')
        await user.click(elt2)
        await user.click(elt3)
        await user.click(elt2)
        await user.keyboard('{/Control}')
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: ["id3", "id1"] },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    //filter
    it("displays an input when filter", async () => {
        const { getByPlaceholderText } = render(<TreeView lov={lov} filter={true} />);
        getByPlaceholderText("Search field");
    });
    it("does not display an input when filter is off", async () => {
        const { queryAllByPlaceholderText } = render(<TreeView lov={lov} filter={false} />);
        expect(queryAllByPlaceholderText("Search field")).toHaveLength(0);
    });
    it("filters items by name", async () => {
        const { getByPlaceholderText, queryAllByText } = render(<TreeView lov={lov} filter={true} />);
        expect(queryAllByText(/Item /)).toHaveLength(4);
        const search = getByPlaceholderText("Search field");
        await userEvent.type(search, "m 3");
        expect(queryAllByText(/Item /)).toHaveLength(1);
        await userEvent.clear(search);
        expect(queryAllByText(/Item /)).toHaveLength(4);
    });
    // expanded
    it("does not dispatch update message when expanded is boolean", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(<TaipyContext.Provider value={{ state, dispatch }}><TreeView lov={lov} expanded={true} updateVars="expanded=tree_expanded" /></TaipyContext.Provider>);
        const elt = getByText("Item 1");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledTimes(1);
        expect(dispatch).toHaveBeenCalledWith({name: "", payload: {id: undefined, names:["tree_expanded"], refresh: false}, type: "REQUEST_UPDATE"});
    });
    it("does dispatch update message when expanded is not boolean", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(<TaipyContext.Provider value={{ state, dispatch }}><TreeView lov={lov} expanded={[]} updateVars="expanded=tree_expanded" /></TaipyContext.Provider>);
        const elt = getByText("Item 1");
        const icon = elt.parentElement?.querySelector(".MuiTreeItem-iconContainer") || elt;
        await userEvent.click(icon);
        //expect(dispatch).toHaveBeenCalledTimes(2);
        expect(dispatch).toHaveBeenCalledWith({name: "", payload: {id: undefined, names:["tree_expanded"], refresh: false}, type: "REQUEST_UPDATE"});
        expect(dispatch).toHaveBeenCalledWith({name:"tree_expanded", payload: {value: ["id1"]}, type: "SEND_UPDATE_ACTION", propagate: true});
    });
});
