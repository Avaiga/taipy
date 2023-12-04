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
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";

import NavBar from './NavBar';
import { LoV } from "./lovUtils";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

const lov: LoV = [
    ["/", "Root"],
    ["/id1", "Item 1"],
    ["/id2", "Item 2"],
    ["/id3", "Item 3"],
    ["/id4", "Item 4"],
];
const defLov = '[["/", "Root"],["/id10","Default Item"]]';

describe("NavBar Component", () => {
    it("renders", async () => {
        const {getByText} = render(<BrowserRouter><NavBar lov={lov} /></BrowserRouter>);
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("BUTTON");
    })
    it("uses the class", async () => {
        const {getByText} = render(<BrowserRouter><NavBar lov={lov} className="taipy-navbar" /></BrowserRouter>);
        const elt = getByText("Item 1");
        expect(elt.parentElement?.parentElement?.parentElement?.parentElement).toHaveClass("taipy-navbar");
    })
    it("displays the right info for lov vs defaultLov", async () => {
        const { getByText, queryAllByText } = render(<BrowserRouter><NavBar lov={lov} defaultLov={defLov} /></BrowserRouter>);
        getByText("Item 1");
        expect(queryAllByText("Default Item")).toHaveLength(0);
    });
    it("displays the default LoV", async () => {
        const { getByText } = render(<BrowserRouter><NavBar lov={undefined as unknown as []} defaultLov={defLov} /></BrowserRouter>);
        getByText("Default Item");
    });
    it("is disabled", async () => {
        const { getAllByRole } = render(<BrowserRouter><NavBar lov={lov} active={false} /></BrowserRouter>);
        const elts = getAllByRole("tab");
        elts.forEach(elt => expect(elt).toBeDisabled());
    });
    it("is enabled by default", async () => {
        const { getAllByRole } = render(<BrowserRouter><NavBar lov={lov} /></BrowserRouter>);
        const elts = getAllByRole("tab");
        elts.forEach(elt => expect(elt).not.toBeDisabled());
    });
    it("is enabled by active", async () => {
        const { getAllByRole } = render(<BrowserRouter><NavBar lov={lov} active={true} /></BrowserRouter>);
        const elts = getAllByRole("tab");
        elts.forEach(elt => expect(elt).not.toBeDisabled());
    });
    it("dispatch a well formed message", async () => {
        const focusSpy = jest.fn()
        window.open = jest.fn().mockReturnValue({ focus: focusSpy })
        const { getByText } = render(<BrowserRouter><NavBar lov={lov}/></BrowserRouter>);
        const elt = getByText("Item 1");
        await userEvent.click(elt);
        expect(focusSpy).toHaveBeenCalled();
    });
    it("shows a default list when no lov", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = {...INITIAL_STATE, locations: {"/": "/routeloc", "/page1": "/loc1", "/page2": "/loc2"}};
        const { getByText, queryAllByRole } = render(<TaipyContext.Provider value={{ state, dispatch }}>
                <BrowserRouter><NavBar lov={undefined as unknown as LoV}/></BrowserRouter>
            </TaipyContext.Provider>);
        const elt = getByText("loc1");
        const elt2 = getByText("loc2");
        expect(queryAllByRole("tab")).toHaveLength(2);
    });
});
