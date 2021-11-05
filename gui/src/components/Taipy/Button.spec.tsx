import React from "react";
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

import Button from "./Button";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("Button Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Button value="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<Button value="toto" defaultValue="titi" className="taipy-button" />);
        const elt = getByText("toto");
        expect(elt).toHaveClass("taipy-button");
    });
    it("displays the default value", async () => {
        const { getByText } = render(
            <Button defaultValue="titi" value={undefined as unknown as string}  />
        );
        getByText("titi");
    });
    it("is disabled", async () => {
        const { getByText } = render(<Button value="val" active={false} />);
        const elt = getByText("val");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<Button value="val" />);
        const elt = getByText("val");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByText } = render(<Button value="val" active={true} />);
        const elt = getByText("val");
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(<TaipyContext.Provider value={{ state, dispatch }}>
                <Button value="Button" tp_onAction="on_action" />
            </TaipyContext.Provider>);
        const elt = getByText("Button");
        fireEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({"name": "", "payload": {"value": "on_action"}, "type": "SEND_ACTION_ACTION"});
    });
});
