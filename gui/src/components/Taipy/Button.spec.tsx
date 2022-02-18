import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import Button from "./Button";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("Button Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Button label="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<Button label="toto" defaultLabel="titi" className="taipy-button" />);
        const elt = getByText("toto");
        expect(elt).toHaveClass("taipy-button");
    });
    it("displays the default value", async () => {
        const { getByText } = render(
            <Button defaultLabel="titi" label={undefined as unknown as string}  />
        );
        getByText("titi");
    });
    it("displays an image", async () => {
        const { getByAltText } = render(
            <Button defaultLabel={JSON.stringify({path: "/image/fred.png", text: "fred"})} label={undefined as unknown as string} />
        );
        const img = getByAltText("fred");
        expect(img.tagName).toBe("IMG")
    });
    it("is disabled", async () => {
        const { getByText } = render(<Button label="val" active={false} />);
        const elt = getByText("val");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<Button label="val" />);
        const elt = getByText("val");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByText } = render(<Button label="val" active={true} />);
        const elt = getByText("val");
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(<TaipyContext.Provider value={{ state, dispatch }}>
                <Button label="Button" tp_onAction="on_action" />
            </TaipyContext.Provider>);
        const elt = getByText("Button");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({"name": "", "payload": {args: [], action: "on_action"}, "type": "SEND_ACTION_ACTION"});
    });
});
