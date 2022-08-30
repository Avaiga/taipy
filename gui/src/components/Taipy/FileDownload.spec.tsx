/*
 * Copyright 2022 Avaiga Private Limited
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
import { act, fireEvent, render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import FileDownload from "./FileDownload";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("FileDownload Component", () => {
    it("renders", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" />);
        const elt = getByRole("button");
        expect(elt).toBeInTheDocument();
    });
    it("displays the right info for string", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" className="taipy-file-download" />);
        const elt = getByRole("button");
        expect(elt.parentElement).toHaveClass("taipy-file-download");
    });
    it("displays the default content", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" content={undefined as unknown as string} />);
        const elt = getByRole("button");
        const aElt = elt.parentElement?.querySelector("a");
        expect(aElt).toBeEmptyDOMElement();
        expect(aElt?.tagName).toBe("A");
        expect(aElt?.href).toBe("http://localhost/url/toto.png");
    });
    it("displays the default label", async () => {
        const { getByText } = render(
            <FileDownload defaultContent="/url/toto.png" defaultLabel="titi" label={undefined as unknown as string} />
        );
        getByText("titi");
    });
    it("is disabled", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" active={false} />);
        const elt = getByRole("button");
        expect(elt).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" />);
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByRole } = render(<FileDownload defaultContent="/url/toto.png" active={true} tp_onAction="tp" />);
        const elt = getByRole("button");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <FileDownload defaultContent="/url/toto.png" tp_onAction="on_action" />
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
