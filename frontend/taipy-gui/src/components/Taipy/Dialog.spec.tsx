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
import { fireEvent, render } from "@testing-library/react";
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
mockedAxios.get.mockResolvedValue({ data: { jsx_no: '<div key="mock" data-testid="mocked"></div>' } });

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
                <Dialog title="Dialog-Test-Title" page="page" open={true} />
            </HelmetProvider>,
        );
        const elt = getByText("Dialog-Test-Title");
        expect(elt.tagName).toBe("H2");
        expect(mockedAxios.get).toHaveBeenCalled();
    });
    it("renders nothing when value is false", async () => {
        const { queryAllByText } = render(
            <HelmetProvider>
                <Dialog title="Dialog-Test-Title" page="page" open={false} />
            </HelmetProvider>,
        );
        expect(queryAllByText("Dialog-Test-Title")).toHaveLength(0);
        const divs = document.getElementsByTagName("div");
        expect(divs).toHaveLength(1);
        expect(divs[0].childElementCount).toBe(0);
    });
    it("displays the right info for class", async () => {
        const wrapper = render(
            <HelmetProvider>
                <Dialog title="Dialog-Test-Title" page="page" open={true} className="taipy-dialog" />
            </HelmetProvider>,
        );
        const elt = document.querySelector(".MuiDialog-root");
        expect(elt).toHaveClass("taipy-dialog");
    });
    it("displays the default value", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                />
            </HelmetProvider>,
        );
        getByText("Dialog-Test-Title");
    });
    it("doesn't show a button by default", async () => {
        const { getAllByRole } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                />
            </HelmetProvider>,
        );
        expect(getAllByRole("button")).toHaveLength(1);
    });
    it("shows one button when a label set", async () => {
        const { getAllByRole } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                    labels={JSON.stringify(["toto"])}
                />
            </HelmetProvider>,
        );
        expect(getAllByRole("button")).toHaveLength(2);
    });
    it("shows 3 buttons when 3 labels set", async () => {
        const { getAllByRole } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    defaultOpen="true"
                    open={undefined as unknown as boolean}
                    labels={JSON.stringify(["toto", "titi", "toto"])}
                />
            </HelmetProvider>,
        );
        expect(getAllByRole("button")).toHaveLength(4);
    });
    it("is disabled", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    open={true}
                    active={false}
                    labels={JSON.stringify(["testValidate", "testCancel"])}
                />
            </HelmetProvider>,
        );
        expect(getByText("testValidate")).toBeDisabled();
        expect(getByText("testCancel")).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    open={true}
                    labels={JSON.stringify(["testValidate", "testCancel"])}
                />
            </HelmetProvider>,
        );
        expect(getByText("testValidate")).not.toBeDisabled();
        expect(getByText("testCancel")).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByText } = render(
            <HelmetProvider>
                <Dialog
                    title="Dialog-Test-Title"
                    page="page"
                    open={true}
                    active={true}
                    labels={JSON.stringify(["testValidate", "testCancel"])}
                />
            </HelmetProvider>,
        );
        expect(getByText("testValidate")).not.toBeDisabled();
        expect(getByText("testCancel")).not.toBeDisabled();
    });
    it("dispatch a well formed message on close icon press", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByTitle } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        page="page"
                        open={true}
                        active={true}
                        onAction="testValidateAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>,
        );
        await userEvent.click(getByTitle("Close"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { action: "testValidateAction", args: [-1] },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on first button press", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        page="page"
                        open={true}
                        active={true}
                        labels={JSON.stringify(["testValidate", "testCancel"])}
                        onAction="testValidateAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>,
        );
        await userEvent.click(getByText("testValidate"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { action: "testValidateAction", args: [0] },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on third button press", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Dialog
                        id="testId"
                        title="Dialog-Test-Title"
                        page="page"
                        open={true}
                        active={true}
                        labels={JSON.stringify(["testValidate", "testCancel", "Another One"])}
                        onAction="testValidateAction"
                    />
                </HelmetProvider>
            </TaipyContext.Provider>,
        );
        await userEvent.click(getByText("Another One"));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { action: "testValidateAction", args: [2] },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("should log an error when labels prop is not a valid JSON string", () => {
        const consoleSpy = jest.spyOn(console, "info");
        render(<Dialog title={"Dialog-Test-Title"} labels={"not a valid JSON string"} />);
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Error parsing dialog.labels"));
    });
    it("should apply width and height styles when they are provided", async () => {
        const { findByRole } = render(<Dialog title="Dialog-Test-Title" width="500px" height="300px" open={true} />);
        const dialogElement = await findByRole("dialog");
        expect(dialogElement).toHaveStyle({ width: "500px", height: "300px" });
    });
    it("should not apply width and height styles when they are not provided", async () => {
        const { findByRole } = render(<Dialog title="Dialog-Test-Title" open={true} />);
        const dialogElement = await findByRole("dialog");
        const computedStyles = window.getComputedStyle(dialogElement);
        expect(computedStyles.width).not.toBe("500px");
        expect(computedStyles.height).not.toBe("300px");
    });
    it("calls localAction prop when handleAction is triggered", () => {
        const localActionMock = jest.fn();
        const { getByLabelText } = render(
            <Dialog id="test-dialog" title="Test Dialog" localAction={localActionMock} open={true} />,
        );
        const closeButton = getByLabelText("close");
        fireEvent.click(closeButton);
        expect(localActionMock).toHaveBeenCalledWith(-1);
    });
});
