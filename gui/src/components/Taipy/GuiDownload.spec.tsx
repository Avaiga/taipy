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

import GuiDownload from "./GuiDownload";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("GuiDownload Component", () => {
    it("emits a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <GuiDownload download={{ content: "/some/link/to.png", name: "from.png", onAction: "onActionMsg" }} />
            </TaipyContext.Provider>
        );
        await waitFor(() =>
            expect(dispatch).toHaveBeenCalledWith({
                name: "Gui.download",
                payload: { args: ["from.png"], action: "onActionMsg" },
                type: "SEND_ACTION_ACTION",
            })
        );
    });
});
