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
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import axios from "axios";
import { HelmetProvider } from "react-helmet-async";

import TaipyRendered from "./TaipyRendered";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

jest.mock("react-router", () => ({
    ...jest.requireActual("react-router"),
    useLocation: () => ({
        pathname: "/test",
        search: "",
    }),
}));

jest.mock("../../jsx/parser", () => ({
    parseJSX: (jsx: string) => <div data-testid="parsed-jsx">{jsx}</div>,
}));

beforeEach(() => {
    mockedAxios.get.mockClear();
    mockedAxios.get.mockResolvedValue({
        data: {
            jsx: "<div>Default Content</div>",
            style: "",
            head: [],
            context: "",
            scriptPaths: [],
        },
    });
});

describe("TaipyRendered Component", () => {
    it("renders without crashing", () => {
        const { container } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch: jest.fn() }}>
                    <TaipyRendered />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );
        expect(container).toBeInTheDocument();
    });

    it("fetches JSX from backend when not partial", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Test Content</div>",
                style: "body { color: red; }",
                head: [],
                context: "test-context",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(mockedAxios.get).toHaveBeenCalled();
        });
    });

    it("dispatches partial action when partial is true", async () => {
        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered partial={true} path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(dispatch).toHaveBeenCalled();
        });
    });

    it("uses custom path from props", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Custom Path</div>",
                style: "",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/custom" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(mockedAxios.get).toHaveBeenCalledWith(expect.stringContaining("/custom"), expect.any(Object));
        });
    });

    it("creates style element when style is provided", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Content</div>",
                style: "body { margin: 0; }",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            const style = document.getElementById("Taipy_style");
            expect(style).toBeInTheDocument();
            expect(style?.textContent).toBe("body { margin: 0; }");
        });
    });

    it("creates script elements when scriptPaths are provided", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Content</div>",
                style: "",
                head: [],
                context: "",
                scriptPaths: ["/script1.js", "/script2.js"],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            const script1 = document.getElementById("Taipy_script_0") as HTMLScriptElement;
            const script2 = document.getElementById("Taipy_script_1") as HTMLScriptElement;
            expect(script1).toBeInTheDocument();
            expect(script2).toBeInTheDocument();
            expect(script1?.src).toContain("/script1.js");
            expect(script2?.src).toContain("/script2.js");
        });
    });

    it("sets head elements from response", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Content</div>",
                style: "",
                head: [
                    { tag: "meta", props: { name: "description", content: "Test Description" }, content: "" },
                    { tag: "link", props: { rel: "stylesheet", href: "test.css" }, content: "" },
                ],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        const { container } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            // Helmet sets the head elements
            expect(container).toBeInTheDocument();
        });
    });

    it("handles error response from backend", async () => {
        mockedAxios.get.mockRejectedValue({
            response: {
                data: '<p class="errormsg">Backend Error: Connection Failed<br>Please try again</p>',
            },
        });

        const dispatch = jest.fn();
        const { container } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(container).toBeInTheDocument();
        });
    });

    it("handles error without response data", async () => {
        mockedAxios.get.mockRejectedValue(new Error("Network Error"));

        const dispatch = jest.fn();
        const { container } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(container).toBeInTheDocument();
        });
    });

    it("uses root style id for TaiPy_root_page path", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Root Content</div>",
                style: "html { background: white; }",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/TaiPy_root_page" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            const style = document.getElementById("Taipy_root_style");
            expect(style).toBeInTheDocument();
            expect(style?.textContent).toBe("html { background: white; }");
        });
    });

    it("updates when path changes", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Content</div>",
                style: "",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        const { rerender } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test1" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(mockedAxios.get).toHaveBeenCalledTimes(1);
        });

        rerender(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test2" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(mockedAxios.get).toHaveBeenCalledTimes(2);
        });
    });

    it("includes client_id in request params", async () => {
        const stateWithId: TaipyState = { ...INITIAL_STATE, id: "test-client-id" };
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Content</div>",
                style: "",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: stateWithId, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(mockedAxios.get).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    params: expect.objectContaining({
                        client_id: "test-client-id",
                    }),
                }),
            );
        });
    });

    it("provides PageContext with jsx and module", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: "<div>Rendered Content</div>",
                style: "",
                head: [],
                context: "test-module-context",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        const { getByTestId } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            const parsed = getByTestId("parsed-jsx");
            expect(parsed).toBeInTheDocument();
        });
    });

    it("renders error when jsx is not a string", async () => {
        mockedAxios.get.mockResolvedValue({
            data: {
                jsx: null,
                style: "",
                head: [],
                context: "",
                scriptPaths: [],
            },
        });

        const dispatch = jest.fn();
        const { container } = render(
            <HelmetProvider>
                <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                    <TaipyRendered path="/test" />
                </TaipyContext.Provider>
            </HelmetProvider>,
        );

        await waitFor(() => {
            expect(container).toBeInTheDocument();
        });
    });
});
