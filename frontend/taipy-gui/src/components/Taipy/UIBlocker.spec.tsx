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
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({"name": "UIBlocker", "payload": {"action": "action", "args": []}, "type": "SEND_ACTION_ACTION"});
    });
});
