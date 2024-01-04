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

import Image from "./Image";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("Image Component", () => {
    it("renders", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" />);
        const elt = getByRole("img");
        expect(elt.tagName).toBe("IMG");
    });
    it("displays the right info for string", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" className="taipy-image" />);
        const elt = getByRole("img");
        expect(elt).toHaveClass("taipy-image");
    });
    it("displays the default content", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" content={undefined as unknown as string} />);
        const elt = getByRole("img");
        expect(elt.tagName).toBe("IMG");
        expect(elt).toHaveAttribute("src", "/url/toto.png");
    });
    it("displays the default label", async () => {
        const { getByAltText } = render(
            <Image defaultContent="/url/toto.png" defaultLabel="titi" label={undefined as unknown as string} />
        );
        getByAltText("titi");
    });
    it("is disabled", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" active={false} onAction="tp" />);
        const elt = getByRole("button");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" onAction="tp" />);
        const elt = getByRole("button");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" active={true} onAction="tp" />);
        const elt = getByRole("button");
        expect(elt).not.toBeDisabled();
    });
    it("is an image when no action", async () => {
        const { getByRole } = render(<Image defaultContent="/url/toto.png" active={true} defaultLabel="toto" />);
        const elt = getByRole("img");
        expect(elt).toBeInTheDocument();
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Image defaultContent="/url/toto.png" onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByRole("button");
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { args: [], action: "on_action" },
            type: "SEND_ACTION_ACTION",
        });
    });
});
