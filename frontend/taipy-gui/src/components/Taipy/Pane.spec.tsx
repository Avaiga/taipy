/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import axios from "axios";

import Pane from "./Pane";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";
import { HelmetProvider } from "react-helmet-async";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;
mockedAxios.get.mockRejectedValue("Network error: Something went wrong");
mockedAxios.get.mockResolvedValue({ data: { jsx_no: '<div key="mock" data-testid="mocked"></div>' } });

jest.mock("react-router", () => ({
    ...jest.requireActual("react-router"),
    useLocation: () => ({
        pathname: "pathname",
    }),
}));

beforeEach(() => {
    mockedAxios.get.mockClear();
});

describe("Pane Component", () => {
    it("renders when value is true", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toBeInTheDocument();
        expect(mockedAxios.get).toHaveBeenCalled();
    });
    it("renders nothing when value is false", async () => {
        const { queryAllByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} />
            </HelmetProvider>
        );
        expect(queryAllByRole("presentation")).toHaveLength(0);
        const divs = document.getElementsByTagName("div");
        expect(divs).toHaveLength(1);
        expect(divs[0].childElementCount).toBe(0);
    });
    it("displays the right info for class", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} className="taipy-pane" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("taipy-pane");
    });
    it("displays the default value", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" defaultOpen="true" open={undefined as unknown as boolean} />
            </HelmetProvider>
        );
        expect(getByRole("presentation")).toBeInTheDocument();
    });
    it("is disabled", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane page="page" open={true} active={false} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && (await userEvent.click(elt));
    });
    it("is enabled by default", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane page="page" open={true} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && (await userEvent.click(elt));
        expect(dispatch).toHaveBeenCalled();
    });
    it("is enabled by active", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane page="page" open={true} active={true} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && (await userEvent.click(elt));
        expect(dispatch).toHaveBeenCalled();
    });
    it("persistent is disabled", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane page="page" open={true} active={false} persistent={true} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeNull();
        const but = getByRole("button");
        expect(but).toBeDisabled();
    });
    it("dispatch a well formed message on close", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane id="testId" page="page" open={true} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && (await userEvent.click(elt));
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { action: "testCloseAction", args: [false] },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on close for persistent", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane id="testId" page="page" open={true} persistent={true} updateVarName="varname" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeNull();
        const but = getByRole("button");
        await userEvent.click(but);
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: false },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("shows a button when closed with property", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane page="page" open={false} showButton={true} persistent={true} onClose="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeNull();
        const but = getByRole("button");
        expect(but).not.toBeDisabled();
    });
    it("anchors to the left when no anchor is set", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("MuiDrawer-root");
        expect(elt).toHaveClass("MuiDrawer-anchorLeft");
    });
    it("anchors to the left when anchor is set to 'l'", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} anchor="l" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("MuiDrawer-anchorLeft");
    });
    it("anchors to the right when anchor is set to 'right'", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} anchor="right" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("MuiDrawer-anchorRight");
    });
    it("anchors to the top when anchor is set to 'top'", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} anchor="top" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("MuiDrawer-anchorTop");
    });
    it("anchors to the bottom when anchor is set to 'bottom'", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={true} anchor="bottom" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("MuiDrawer-anchorBottom");
    });
    it("renders with a title", async () => {
        render(
            <HelmetProvider>
                <Pane page="page" open={true} persistent={true} defaultTitle="pane-title-test" />
            </HelmetProvider>
        );
        const elt = document.querySelector(".MuiBox-root");
        expect(elt).toHaveTextContent("pane-title-test");
    });
    it("renders with a dynamic title", async () => {
        render(
            <HelmetProvider>
                <Pane page="page" open={true} persistent={true} defaultTitle="pane-title-test" title="pane-dynamic-title-test" />
            </HelmetProvider>
        );
        const elt = document.querySelector(".MuiBox-root");
        expect(elt).toHaveTextContent("pane-dynamic-title-test");
    });
    it("shows correct icon when closed with left anchor", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} anchor="left" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        expect(but).toBeInTheDocument();
        const svg = but.querySelector("svg");
        expect(svg).toHaveAttribute("data-testid", "ChevronRightIcon");
    });
    it("shows correct icon when closed with right anchor", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} anchor="right" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        const svg = but.querySelector("svg");
        expect(svg).toHaveAttribute("data-testid", "ChevronLeftIcon");
    });
    it("shows correct icon when closed with top anchor", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} anchor="top" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        const svg = but.querySelector("svg");
        expect(svg).toHaveAttribute("data-testid", "ExpandMoreIcon");
    });
    it("shows correct icon when closed with bottom anchor", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} anchor="bottom" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        const svg = but.querySelector("svg");
        expect(svg).toHaveAttribute("data-testid", "ExpandLessIcon");
    });
    it("shows hover text when closed", async () => {
        const { getByRole, findByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} defaultHoverText="Test hover text" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        await userEvent.hover(but);
        const tooltip = await findByRole("tooltip");
        expect(tooltip).toHaveTextContent("Test hover text");
    });
    it("shows dynamic hover text when closed", async () => {
        const { getByRole, findByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} defaultHoverText="Default hover" hoverText="Dynamic hover" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        await userEvent.hover(but);
        const tooltip = await findByRole("tooltip");
        expect(tooltip).toHaveTextContent("Dynamic hover");
    });
    it("shows title and hover text combined when closed", async () => {
        const { getByRole, findByRole } = render(
            <HelmetProvider>
                <Pane page="page" open={false} showButton={true} defaultTitle="Pane Title" defaultHoverText="Hover text" />
            </HelmetProvider>
        );
        const but = getByRole("button");
        await userEvent.hover(but);
        const tooltip = await findByRole("tooltip");
        expect(tooltip).toHaveTextContent("Pane Title");
        expect(tooltip).toHaveTextContent("Hover text");
    });
});
