import React from "react";
import { act, fireEvent, render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import FileSelector from "./FileSelector";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { uploadFile } from "../../workers/fileupload";

// need to mock the worker as import.meta.url is not supported yet by jest
jest.mock("../../workers/fileupload", () => {
    return {
        __esModule: true,
        uploadFile: (
            varName: string,
            files: FileList,
            progressCallback: (val: number) => void,
            id: string,
            uploadUrl: string
        ) => new Promise((resolve, reject) => {
            resolve("mocked");
        }),
    };
});

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
    it("dispatch a well formed message on file selection", async () => {
        const user = userEvent.setup();
        const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <FileSelector label="FileSelector" tp_onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByText("FileSelector");
        const inputElt = elt.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        waitFor(() => expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: "on_action" },
            type: "SEND_ACTION_ACTION",
        }));
        inputElt && user.upload(inputElt, file);
    });
    it("dispatch a well formed message on file drop", async () => {
        const file = new File(['(⌐□_□)'], 'chucknorris2.png', { type: 'image/png' });
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <FileSelector label="FileSelectorDrop" tp_onAction="on_action" />
            </TaipyContext.Provider>
        );
        const elt = getByRole("button");
        const inputElt = elt.parentElement?.querySelector("input");
        expect(inputElt).toBeInTheDocument();
        waitFor(() => expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: "on_action" },
            type: "SEND_ACTION_ACTION",
        }));
        inputElt && fireEvent.drop(inputElt, {
            dataTransfer: {
              files: [file],
            },
          })
    });
});
