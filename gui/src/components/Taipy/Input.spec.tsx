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

import Input from "./Input";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("Input Component", () => {
    it("renders", async () => {
        const { getByDisplayValue } = render(<Input type="text" value="toto" />);
        const elt = getByDisplayValue("toto");
        expect(elt.tagName).toBe("INPUT");
    });
    it("displays the right info for string", async () => {
        const { getByDisplayValue } = render(
            <Input value="toto" type="text" defaultValue="titi" className="taipy-input" />
        );
        const elt = getByDisplayValue("toto");
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-input");
    });
    it("displays the default value", async () => {
        const { getByDisplayValue } = render(
            <Input defaultValue="titi" value={undefined as unknown as string} type="text" />
        );
        getByDisplayValue("titi");
    });
    it("is disabled", async () => {
        const { getByDisplayValue } = render(<Input value="val" type="text" active={false} />);
        const elt = getByDisplayValue("val");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByDisplayValue } = render(<Input value="val" type="text" />);
        const elt = getByDisplayValue("val");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByDisplayValue } = render(<Input value="val" type="text" active={true} />);
        const elt = getByDisplayValue("val");
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Input value="Val" type="text" updateVarName="varname" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("Val");
        await userEvent.clear(elt);
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: "" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("dispatch a well formed message on enter", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Input value="Val" type="text" updateVarName="varname" onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("Val");
        await userEvent.click(elt);
        await userEvent.keyboard("data{Enter}");
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "",
            payload: { action: "on_action", args: ["Enter", "varname", "Valdata"] },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a no action message on unsupported key", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Input value="Val" type="text" updateVarName="varname" onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("Val");
        await userEvent.click(elt);
        await userEvent.keyboard("data{Escape}");
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: "Valdata" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});

describe("Number Component", () => {
    it("renders", async () => {
        const { getByDisplayValue } = render(<Input type="number" value="12" />);
        const elt = getByDisplayValue("12");
        expect(elt.tagName).toBe("INPUT");
    });
    it("displays the right info for string", async () => {
        const { getByDisplayValue } = render(
            <Input value="12" type="number" defaultValue="1" className="taipy-number" />
        );
        const elt = getByDisplayValue(12);
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-number");
    });
    it("displays the default value", async () => {
        const { getByDisplayValue } = render(
            <Input defaultValue="1" value={undefined as unknown as string} type="number" />
        );
        getByDisplayValue("1");
    });
    it("is disabled", async () => {
        const { getByDisplayValue } = render(<Input value={"33"} type="number" active={false} />);
        const elt = getByDisplayValue("33");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByDisplayValue } = render(<Input value={"33"} type="number" />);
        const elt = getByDisplayValue("33");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByDisplayValue } = render(<Input value={"33"} type="number" active={true} />);
        const elt = getByDisplayValue("33");
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Input value={"33"} type="number" updateVarName="varname" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("33");
        await userEvent.clear(elt);
        await userEvent.type(elt, "666");
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: "666" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    xit("shows 0", async () => {
    //not working cf. https://github.com/testing-library/user-event/issues/1066
    const { getByDisplayValue, rerender } = render(<Input value={"0"} type="number" />);
        const elt = getByDisplayValue("0") as HTMLInputElement;
        expect(elt).toBeInTheDocument();
        await userEvent.type(elt, "{ArrowUp}");
        expect(elt.value).toBe("1");
        await userEvent.type(elt, "{ArrowDown}");
        expect(elt.value).toBe("0");
    });
});
