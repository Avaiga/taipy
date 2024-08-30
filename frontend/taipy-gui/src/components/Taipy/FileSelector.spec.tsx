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
import { uploadFile } from "../../workers/fileupload";

jest.mock("../../workers/fileupload", () => ({
    uploadFile: jest.fn().mockResolvedValue("mocked response"), // returns a Promise that resolves to 'mocked response'
}));

describe("FileSelector Component", () => {
    it("renders", async () => {
        const { getByText } = render(<FileSelector label="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("SPAN");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<FileSelector label="toto" defaultLabel="titi" className="taipy-file-selector" />);
        const elt = getByText("toto");
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-file-selector");
    });
    it("displays the default value", async () => {
        const { getByText } = render(<FileSelector defaultLabel="titi" label={undefined as unknown as string} />);
        getByText("titi");
    });
    it("displays with width=70%", async () => {
        const { getByText } = render(<FileSelector label="toto" width="70%" />);
        const elt = getByText("toto");
        expect(elt).toHaveStyle("width: 70%");
    });
    it("displays with width=500", async () => {
        const { getByText } = render(<FileSelector label="toto" width={500} />);
        const elt = getByText("toto");
        expect(elt).toHaveStyle("width: 500px");
    });
    it("is disabled", async () => {
        const { getByText } = render(<FileSelector label="val" active={false} />);
        const elt = getByText("val");
        expect(elt).toHaveClass("Mui-disabled");
        expect(elt.parentElement?.parentElement?.querySelector("input")).toBeDisabled();
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
        const inputElt = elt.parentElement?.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        inputElt && (await userEvent.upload(inputElt, file));
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { args: [], action: "on_action" },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a specific text on file drop", async () => {
        const file = new File(["(⌐□_□)"], "chucknorris2.png", { type: "image/png" });
        const { getByRole, getByText } = render(<FileSelector label="FileSelectorDrop" />);
        const elt = getByRole("button");
        const inputElt = elt.parentElement?.parentElement?.querySelector("input");
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
        const { getByRole, getByText } = render(
            <FileSelector label="FileSelectorDrop" dropMessage="drop here those files" />
        );
        const elt = getByRole("button");
        const inputElt = elt.parentElement?.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        waitFor(() => getByText("drop here those files"));
        inputElt &&
            fireEvent.drop(inputElt, {
                dataTransfer: {
                    files: [file],
                },
            });
    });
    it("handles drag over event", () => {
        const { getByRole } = render(<FileSelector label="FileSelectorDrag" />);
        const fileSelector = getByRole("button");

        // Create a mock DragEvent and add a dataTransfer object
        const mockEvent = new Event("dragover", { bubbles: true }) as unknown as DragEvent;
        Object.assign(mockEvent, {
            dataTransfer: {
                dropEffect: "",
            },
        });

        // Dispatch the mock event
        fireEvent(fileSelector, mockEvent);

        // Add assertion to check if dropEffect is set to "copy"
        expect(mockEvent.dataTransfer!.dropEffect).toBe("copy");
    });

    it("handles file drop", async () => {
        // Create a mock file
        const file = new File(["(⌐□_□)"], "chucknorris.png", { type: "image/png" });

        const { getByRole } = render(<FileSelector label="FileSelectorDrop" />);
        const elt = getByRole("button");
        // Create a mock DragEvent and add the mock file to the event's dataTransfer.files property
        const mockEvent = new Event("drop", { bubbles: true }) as unknown as DragEvent;
        Object.assign(mockEvent, {
            dataTransfer: {
                files: [file],
            },
        });
        // Dispatch the mock event
        fireEvent(elt, mockEvent);
        expect(uploadFile).toHaveBeenCalledTimes(1);
    });

    it("resets dropLabel and dropSx on drag leave", async () => {
        const { getByRole } = render(<FileSelector />);
        const elt = getByRole("button");

        // Create a mock DragEvent
        const mockEvent = new Event("dragleave", { bubbles: true }) as unknown as DragEvent;

        // Dispatch the mock event
        fireEvent(elt, mockEvent);

        // Add assertions to check if dropLabel and dropSx have been reset
        const labelElement = elt.querySelector("span");
        expect(labelElement!.textContent).toBe("");
        expect(elt).toHaveStyle("min-width: 0px");
    });

    it("checks if notification is dispatched on file upload completion", async () => {
        const mockDispatch = jest.fn();
        const { getByLabelText } = render(
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch: mockDispatch }}>
                <FileSelector label="FileSelector" notify={true} />
            </TaipyContext.Provider>
        );

        // Simulate file upload
        const file = new File(["(⌐□_□)"], "chucknorris.png", { type: "image/png" });
        const inputElement = getByLabelText("FileSelector");
        fireEvent.change(inputElement, { target: { files: [file] } });

        // Wait for the upload to complete
        await waitFor(() => expect(mockDispatch).toHaveBeenCalled());

        // Check if the alert action has been dispatched
        expect(mockDispatch).toHaveBeenCalledWith(
            expect.objectContaining({
                type: "SET_ALERT",
                atype: "success",
                duration: 3000,
                message: "mocked response",
                system: false,
            })
        );
    });

    it("checks if error notification is dispatched on file upload failure", async () => {
        const mockUploadFile = uploadFile as jest.Mock;

        mockUploadFile.mockImplementation(() => {
            return new Promise((resolve, reject) => {
                reject("Upload failed");
            });
        });

        const mockDispatch = jest.fn();
        const { getByLabelText } = render(
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch: mockDispatch }}>
                <FileSelector label="FileSelector" notify={true} />
            </TaipyContext.Provider>
        );

        // Simulate file upload
        const file = new File(["(⌐□_□)"], "chucknorris.png", { type: "image/png" });
        const inputElement = getByLabelText("FileSelector");
        fireEvent.change(inputElement, { target: { files: [file] } });

        // Wait for the upload to complete
        await waitFor(() => expect(mockDispatch).toHaveBeenCalled());

        // Check if the alert action has been dispatched
        expect(mockDispatch).toHaveBeenCalledWith(
            expect.objectContaining({
                type: "SET_ALERT",
                atype: "error",
                duration: 3000,
                message: "Upload failed",
                system: false,
            })
        );
    });

    it("checks if dispatch is called correctly", async () => {
        // Mock the uploadFile function to resolve with a success message
        (uploadFile as jest.Mock).mockImplementation(() => Promise.resolve("mocked response"));

        const mockDispatch = jest.fn();
        const { getByLabelText, queryByRole } = render(
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch: mockDispatch }}>
                <FileSelector label="FileSelector" notify={true} onAction="testAction" />
            </TaipyContext.Provider>
        );

        // Simulate file upload
        const file = new File(["(⌐□_□)"], "chucknorris.png", { type: "image/png" });
        const inputElement = getByLabelText("FileSelector");
        fireEvent.change(inputElement, { target: { files: [file] } });

        // Check if the progress bar is displayed during the upload process
        expect(queryByRole("progressbar")).toBeInTheDocument();

        // Wait for the upload to complete
        await waitFor(() => expect(mockDispatch).toHaveBeenCalled());

        // Check if the progress bar is not displayed after the upload is completed
        expect(queryByRole("progressbar")).not.toBeInTheDocument();

        // Check if the dispatch function has been called with the correct action
        expect(mockDispatch).toHaveBeenCalledWith(
            expect.objectContaining({
                type: "SEND_ACTION_ACTION",
                name: "",
                payload: { args: [], action: "testAction" },
            })
        );
    });

    it("checks if no action is taken when no file is uploaded", async () => {
        const mockDispatch = jest.fn();
        const { getByLabelText } = render(
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch: mockDispatch }}>
                <FileSelector label="FileSelector" notify={true} />
            </TaipyContext.Provider>
        );

        // Simulate file upload without providing a file
        const inputElement = getByLabelText("FileSelector");
        fireEvent.change(inputElement, { target: { files: [] } });

        // Check if the dispatch function has not been called
        expect(mockDispatch).not.toHaveBeenCalled();
    });
});
