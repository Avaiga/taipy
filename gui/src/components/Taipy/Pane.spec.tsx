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

describe("Pane Component", () => {
    it("renders when value is true", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane pageId="pageId" open={true} />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toBeInTheDocument();
        expect(mockedAxios.get).toHaveBeenCalled();
    });
    it("renders nothing when value is false", async () => {
        const { queryAllByRole } = render(
            <HelmetProvider>
                <Pane pageId="pageId" open={false} />
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
                <Pane pageId="pageId" open={true} className="taipy-pane" />
            </HelmetProvider>
        );
        const elt = getByRole("presentation");
        expect(elt).toHaveClass("taipy-pane");
    });
    it("displays the default value", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Pane pageId="pageId" defaultOpen="true" open={undefined as unknown as boolean} />
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
                    <Pane pageId="pageId" open={true} active={false} closeAction="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && userEvent.click(elt);
        expect(dispatch).not.toHaveBeenCalled();
    });
    it("is enabled by default", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane pageId="pageId" open={true} closeAction="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && userEvent.click(elt);
        expect(dispatch).toHaveBeenCalled();
    });
    it("is enabled by active", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane pageId="pageId" open={true} active={true} closeAction="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && userEvent.click(elt);
        expect(dispatch).toHaveBeenCalled();
    });
    it("persistent is disabled", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane pageId="pageId" open={true} active={false} persistent={true} closeAction="testCloseAction" />
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
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane id="testId" pageId="pageId" open={true} closeAction="testCloseAction" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeInTheDocument();
        elt && userEvent.click(elt);
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "testId",
            payload: { value: "testCloseAction" },
            type: "SEND_ACTION_ACTION",
        });
    });
    it("dispatch a well formed message on close for persistent", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <HelmetProvider>
                    <Pane id="testId" pageId="pageId" open={true} persistent={true} tp_varname="varname" />
                </HelmetProvider>
            </TaipyContext.Provider>
        );
        const elt = document.querySelector(".MuiBackdrop-root");
        expect(elt).toBeNull();
        const but = getByRole("button");
        userEvent.click(but);
        expect(dispatch).toHaveBeenLastCalledWith({
            name: "varname",
            payload: { value: false },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
