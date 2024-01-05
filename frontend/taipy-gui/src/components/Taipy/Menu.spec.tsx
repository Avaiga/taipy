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

import Menu from "./Menu";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";
import { LovItem } from "../../utils/lov";

const lov: LovItem[] = [
    {id: "id1", item: "Item 1"},
    {id: "id2", item:"Item 2"},
    {id: "id3", item:"Item 3"},
    {id: "id4", item:"Item 4"},
];

const imageItem: LovItem = {id: "ii1", item: { path: "/img/fred.png", text: "Image" }};

describe("Menu Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Menu lov={lov} />);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("SPAN");
    });
    it("uses the class", async () => {
        const { getByText } = render(<Menu lov={lov} className="taipy-menu" />);
        const elt = getByText("Item 1");
        expect(elt.closest(".taipy-menu")).not.toBeNull();
    });
    it("can display an avatar with initials", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByText } = render(<Menu lov={lovWithImage} />);
        const elt = getByText("I2");
        expect(elt.tagName).toBe("DIV");
    });
    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(<Menu lov={lovWithImage} />);
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<Menu lov={lov} active={false} />);
        const elts = getAllByRole("button");
        elts.forEach((elt, idx) => idx > 0 && expect(elt).toHaveClass("Mui-disabled"));
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<Menu lov={lov} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<Menu lov={lov} active={true} />);
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });
    it("can disable a specific item", async () => {
        const { getByText } = render(<Menu lov={lov} inactiveIds={[lov[0].id]} />);
        const elt = getByText(lov[0].item as string);
        const button = elt.closest('[role="button"]')
        expect(button).toHaveClass("Mui-disabled");
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Menu lov={lov} onAction="action" />
            </TaipyContext.Provider>
        );
        const elt = getByText(lov[0].item as string);
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "menu",
            payload: { action: "action", args: [lov[0].id] },
            type: "SEND_ACTION_ACTION",
        });
    });
});
