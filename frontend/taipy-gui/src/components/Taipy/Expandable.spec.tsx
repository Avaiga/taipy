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
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Expandable from "./Expandable";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

describe("Expandable Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Expandable title="foo">bar</Expandable>);
        const elt = getByText("foo");
        expect(elt.tagName).toBe("DIV");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(
            <Expandable title="foo" defaultTitle="bar" className="taipy-expandable">
                bar
            </Expandable>
        );
        const elt = getByText("foo");
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-expandable");
    });
    it("displays the default value", async () => {
        const { getByText } = render(
            <Expandable defaultTitle="bar" title={undefined as unknown as string}>
                foobar
            </Expandable>
        );
        getByText("bar");
    });
    it("is disabled", async () => {
        const { getByRole } = render(
            <Expandable title="foo" active={false}>
                bar
            </Expandable>
        );
        const elt = getByRole("button");
        expect(elt).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByRole } = render(<Expandable title="foo">bar</Expandable>);
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByRole } = render(
            <Expandable title="foo" active={true}>
                bar
            </Expandable>
        );
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is collapsed", async () => {
        const { getByText } = render(
            <Expandable title="foo" expanded={false}>
                bar
            </Expandable>
        );
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).toHaveClass("MuiCollapse-hidden");
        expect(div).toHaveStyle({ height: "0px" });
    });
    it("is not collapsed by default", async () => {
        const { getByText } = render(<Expandable title="foo">bar</Expandable>);
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).not.toHaveClass("MuiCollapse-hidden");
        expect(div).not.toHaveStyle({ height: "0px" });
    });
    it("is not collapsed by expanded", async () => {
        const { getByText } = render(
            <Expandable title="foo" expanded={true}>
                bar
            </Expandable>
        );
        const elt = getByText("bar");
        const div = elt.closest("div.MuiCollapse-root");
        expect(div).toBeInTheDocument();
        expect(div).not.toHaveClass("MuiCollapse-hidden");
        expect(div).not.toHaveStyle({ height: "0px" });
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Expandable title="foo" expanded={true} updateVars="expanded=expanded_var">
                    bar
                </Expandable>
            </TaipyContext.Provider>
        );
        const elt = getByText("foo");
        const div = elt.nextElementSibling;
        div && await userEvent.click(div);
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "expanded_var",
            payload: { value: false },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
