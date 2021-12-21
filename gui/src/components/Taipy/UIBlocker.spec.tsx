import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import UIBlocker from "./UIBlocker";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE, BlockMessage } from "../../context/taipyReducers";

const blockWithCancel: BlockMessage = {message: "message", close: false, noCancel: false, action:"action"}

describe("UIBlocker Component", () => {
    it("renders", async () => {
        const { getByText } = render(<UIBlocker block={blockWithCancel}/>);
        const elt = getByText("Cancel");
        expect(elt.tagName).toBe("BUTTON");
    });
    it("displays the right className", async () => {
        const { getByText } = render(<UIBlocker block={blockWithCancel} />);
        const elt = getByText("Cancel");
        expect(elt.parentElement).toHaveClass("taipy-UIBlocker");
    });
    it("doesn't display by default", async () => {
        const { queryAllByAltText } = render(
            <UIBlocker />
        );
        expect(queryAllByAltText("Cancel")).toHaveLength(0);
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(<TaipyContext.Provider value={{ state, dispatch }}>
                <UIBlocker block={blockWithCancel} />
            </TaipyContext.Provider>);
        const elt = getByText("Cancel");
        userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({"name": "UIBlocker", "payload": {"value": "action"}, "type": "SEND_ACTION_ACTION"});
    });
});
