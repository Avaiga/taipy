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
import { fireEvent, render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import FileSelector from "./FileSelector";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("FileSelector Component", () => {
    it("renders", async () => {
        const { getByText } = render(<FileSelector label="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("SPAN");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<FileSelector label="toto" defaultLabel="titi" className="taipy-file-selector" />);
        const elt = getByText("toto");
        expect(elt.parentElement).toHaveClass("taipy-file-selector");
    });
    it("displays the default value", async () => {
        const { getByText } = render(<FileSelector defaultLabel="titi" label={undefined as unknown as string} />);
        getByText("titi");
    });
    it("is disabled", async () => {
        const { getByText } = render(<FileSelector label="val" active={false} />);
        const elt = getByText("val");
        expect(elt).toHaveClass("Mui-disabled");
    });
    it("is enabled by default", async () => {
        const { getByText } = render(<FileSelector label="val" />);
        const elt = getByText("val");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    it("is enabled by active", async () => {
        const { getByText } = render(<FileSelector label="val" active={true} />);
        const elt = getByText("val");
        expect(elt).not.toHaveClass("Mui-disabled");
    });
    //looks like userEvent upload does not fire onchange
    xit("dispatch a well formed message on file selection", async () => {
        const file = new File(["(⌐□_□)"], "chucknorris.png", { type: "image/png" });
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <FileSelector label="FileSelector" onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByText("FileSelector");
        const inputElt = elt.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        inputElt && await userEvent.upload(inputElt, file);
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { args: [], action: "on_action" },
            type: "SEND_ACTION_ACTION",
        })
    });
    it("dispatch a specific text on file drop", async () => {
        const file = new File(["(⌐□_□)"], "chucknorris2.png", { type: "image/png" });
        const { getByRole, getByText } = render(<FileSelector label="FileSelectorDrop" />);
        const elt = getByRole("button");
        const inputElt = elt.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        waitFor(() => getByText("Drop here to Upload"));
        inputElt &&
            fireEvent.drop(inputElt, {
                dataTransfer: {
                    files: [file],
                },
            });
    });
    it("displays a dropped custom message", async () => {
        const file = new File(["(⌐□_□)"], "chucknorris2.png", { type: "image/png" });
        const { getByRole, getByText } = render(<FileSelector label="FileSelectorDrop" dropMessage="drop here those files" />);
        const elt = getByRole("button");
        const inputElt = elt.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        waitFor(() => getByText("drop here those files"));
        inputElt &&
            fireEvent.drop(inputElt, {
                dataTransfer: {
                    files: [file],
                },
            });
    });
});
