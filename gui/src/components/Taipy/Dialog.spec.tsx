import React from "react";
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import axios from "axios";

import Dialog from "./Dialog";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { HelmetProvider } from "react-helmet-async";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;
mockedAxios.get.mockRejectedValue("Network error: Something went wrong");
mockedAxios.get.mockResolvedValue({ data: { jsx1: '<div key="mock" data-testid="mocked"></div>' } });

jest.mock("react-router-dom", () => ({
    ...jest.requireActual("react-router-dom"),
    useLocation: () => ({
        pathname: "pathname",
    }),
}));

beforeEach(() => {
    mockedAxios.get.mockClear();
});

describe("Dialog Component", () => {
    it("renders when value is true", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog title="Dialog-Test-Title" pageId="pageId" open={true} />
            </HelmetProvider>
        );
        const elt = getByText("Dialog-Test-Title");
        expect(elt.tagName).toBe("H2");
        expect(mockedAxios.get).toHaveBeenCalled();
    });
    it("renders nothing when value is false", async () => {
        const { queryAllByText } = render(
            <HelmetProvider>
                <Dialog title="Dialog-Test-Title" pageId="pageId" open={false} />
            </HelmetProvider>
        );
        expect(queryAllByText("Dialog-Test-Title")).toHaveLength(0);
        const divs = document.getElementsByTagName("div");
        expect(divs).toHaveLength(1);
        expect(divs[0].childElementCount).toBe(0);
    });
    it("displays the right info for class", async () => {
        const wrapper = render(
            <HelmetProvider>
                <Dialog title="Dialog-Test-Title" pageId="pageId" open={true} className="taipy-dialog" />
            </HelmetProvider>
        );
        const elt = document.querySelector(".MuiDialog-root");
        expect(elt).toHaveClass("taipy-dialog");
    });
    it("displays the default value", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                />
            </HelmetProvider>
        );
        getByText("Dialog-Test-Title");
    });
    it("doesn't show the cancel button by default", async () => {
        const { getAllByRole } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                />
            </HelmetProvider>
        );
        expect(getAllByRole("button")).toHaveLength(2);
    });
    it("shows the cancel button when cancel action is set", async () => {
        const { getAllByRole } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                    cancelAction={"testCancelAction"}
                />
            </HelmetProvider>
        );
        expect(getAllByRole("button")).toHaveLength(3);
    });
    it("is disabled", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    open={true}
                    active={false}
                    validateLabel="testValidate"
                    cancelAction="testCancelAction"
                    cancelLabel="testCancel"
                />
            </HelmetProvider>
        );
        expect(getByText("testValidate")).toBeDisabled();
        expect(getByText("testCancel")).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    open={true}
                    validateLabel="testValidate"
                    cancelAction="testCancelAction"
                    cancelLabel="testCancel"
                />
            </HelmetProvider>
        );
        expect(getByText("testValidate")).not.toBeDisabled();
        expect(getByText("testCancel")).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    pageId="pageId"
                    open={true}
                    active={true}
                    validateLabel="testValidate"
                    cancelAction="testCancelAction"
                    cancelLabel="testCancel"
                />
            </HelmetProvider>
        );
        expect(getByText("testValidate")).not.toBeDisabled();
        expect(getByText("testCancel")).not.toBeDisabled();
    });
    it("dispatch a well formed message on validate", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        pageId="pageId"
                        open={true}
                        active={true}
                        validateLabel="testValidate"
                        validateAction="testValidateAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        userEvent.click(getByText("testValidate"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { value: "testValidateAction" },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on cancel", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        pageId="pageId"
                        open={true}
                        active={true}
                        cancelLabel="testCancel"
                        cancelAction="testCancelAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        userEvent.click(getByText("testCancel"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { value: "testCancelAction" },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on close with no cancel", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTestId } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        pageId="pageId"
                        open={true}
                        active={true}
                        validateAction="testValidateAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        userEvent.click(getByTestId("CloseIcon"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { value: "testValidateAction" },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on close with cancel defined", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTestId } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        pageId="pageId"
                        open={true}
                        active={true}
                        cancelLabel="testCancel"
                        cancelAction="testCancelAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        userEvent.click(getByTestId("CloseIcon"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { value: "testCancelAction" },
            type: "SEND_ACTION_ACTION",
        });
    });
});
