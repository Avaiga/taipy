import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
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
        userEvent.clear(elt);
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
                <Input value="Val" type="text" updateVarName="varname" tp_onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("Val");
        userEvent.click(elt);
        userEvent.keyboard("data{Enter}");
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
                <Input value="Val" type="text" updateVarName="varname" tp_onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("Val");
        userEvent.click(elt);
        userEvent.keyboard("data{Escape}");
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
        userEvent.clear(elt);
        userEvent.type(elt, "666");
        await waitFor(() => expect(dispatch).toHaveBeenCalled());
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: "666" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
