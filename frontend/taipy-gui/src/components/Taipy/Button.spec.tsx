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
                <Button label="Button" onAction="on_action" />
            </TaipyContext.Provider>);
        const elt = getByText("Button");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({"name": "", "payload": {args: [], action: "on_action"}, "type": "SEND_ACTION_ACTION"});
    });
});
