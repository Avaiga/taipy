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

import Toggle from "./Toggle";
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

describe("Toggle Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Toggle lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("P");
    });
    it("uses the class", async () => {
        const { getByText } = render(<Toggle lov={lov} className="taipy-toggle" />);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement?.parentElement).toHaveClass("taipy-toggle");
    });
    it("shows a label", async () => {
        const { getByText } = render(<Toggle lov={lov} label="label" />);
        const elt = getByText("label");
        expect(elt.tagName).toBe("P");
    });
    it("doesn't show a label", async () => {
        render(<Toggle lov={lov} />);
        const boxDiv = document.querySelector(".MuiBox-root");
        const eltPs = boxDiv?.querySelectorAll("p");
        //We don't want p tags as children of the main Box ie no label
        eltPs?.forEach((p) => expect(p.parentElement).not.toBe(boxDiv));
    });
    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(<Toggle lov={lovWithImage} />);
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });
    it("displays the right info for lov vs defaultLov", async () => {
        const { getByText, queryAllByText } = render(<Toggle lov={lov} defaultLov={defLov} />);
        getByText("Item 1");
        expect(queryAllByText("Default Item")).toHaveLength(0);
    });
    it("displays the default LoV", async () => {
        const { getByText } = render(<Toggle lov={undefined as unknown as []} defaultLov={defLov} />);
        getByText("Default Item");
    });
    it("shows a selection at start", async () => {
        const { getByText } = render(<Toggle defaultValue="id1" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement).toHaveClass("Mui-selected");
    });
    it("shows a selection at start through value", async () => {
        const { getByText } = render(<Toggle defaultValue="id1" value="id2" lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.parentElement).not.toHaveClass("Mui-selected");
        const elt2 = getByText("Item 2");
        expect(elt2.parentElement).toHaveClass("Mui-selected");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<Toggle lov={lov} active={false} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).toBeDisabled());
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<Toggle lov={lov} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toBeDisabled());
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<Toggle lov={lov} active={true} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toBeDisabled());
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Toggle lov={lov} updateVarName="varname" />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 1");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "varname",
            payload: { value: "id1" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("dispatch unselected_value on deselection when allowUnselect", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Toggle lov={lov} updateVarName="varname" unselectedValue="uv" value="id2" allowUnselect={true} />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 2");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "varname",
            payload: { value: "uv" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("dispatch nothing on deselection by default", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Toggle lov={lov} updateVarName="varname" unselectedValue="uv" value="id2" />
            </TaipyContext.Provider>
        );
        const elt = getByText("Item 2");
        await userEvent.click(elt);
        expect(dispatch).not.toHaveBeenCalled();
    });

    describe("As Switch", () => {
        it("renders", async () => {
            const { getByText } = render(<Toggle defaultValue={false as unknown as string} label="switch" />);
            const elt = getByText("switch");
            expect(elt.tagName).toBe("SPAN");
        });
        it("uses the class", async () => {
            const { getByText } = render(<Toggle defaultValue={false as unknown as string} label="switch" className="taipy-toggle" />);
            const elt = getByText("switch");
            expect(elt.parentElement).toHaveClass("taipy-toggle-switch");
        });
        it("shows a selection at start", async () => {
            const { getByText } = render(<Toggle defaultValue={true as unknown as string} label="switch" />);
            const elt = getByText("switch");
            expect(elt.parentElement?.querySelector(".MuiSwitch-switchBase")).toHaveClass("Mui-checked");
        });
        it("shows a selection at start through value", async () => {
            const { getByText } = render(<Toggle value={true as unknown as string} defaultValue={false as unknown as string} label="switch" />);
            const elt = getByText("switch");
            expect(elt.parentElement?.querySelector(".MuiSwitch-switchBase")).toHaveClass("Mui-checked");
        });
        it("is disabled", async () => {
            const { getByText } = render(<Toggle defaultValue={false as unknown as string} label="switch" active={false} />);
            const elt = getByText("switch");
            expect(elt.parentElement?.querySelector("input")).toBeDisabled();
        });
        it("is enabled by default", async () => {
            const { getByText } = render(<Toggle defaultValue={false as unknown as string} label="switch" />);
            const elt = getByText("switch");
            expect(elt.parentElement?.querySelector("input")).not.toBeDisabled();
        });
        it("is enabled by active", async () => {
            const { getByText } = render(<Toggle defaultValue={false as unknown as string} label="switch" active={true} />);
            const elt = getByText("switch");
            expect(elt.parentElement?.querySelector("input")).not.toBeDisabled();
        });
        it("dispatch a well formed message", async () => {
            const dispatch = jest.fn();
            const state: TaipyState = INITIAL_STATE;
            const { getByText } = render(
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Toggle updateVarName="varname" defaultValue={false as unknown as string} label="switch" />
                </TaipyContext.Provider>
            );
            const elt = getByText("switch");
            await userEvent.click(elt);
            expect(dispatch).toHaveBeenCalledWith({
                name: "varname",
                payload: { value: true },
                propagate: true,
                type: "SEND_UPDATE_ACTION",
            });
        });

    });
});
