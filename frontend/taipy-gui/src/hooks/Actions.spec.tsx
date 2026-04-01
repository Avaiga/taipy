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

import React, { PropsWithChildren } from "react";
import { act, renderHook } from "@testing-library/react";

import { useActions, useRequestUpdateOnFirstRender } from "./Actions";
import { INITIAL_STATE } from "../context/taipyReducers";
import { PageContext, TaipyContext } from "../context/taipyContext";

describe("useActions", () => {
    it("dispatches an Action action", () => {
        const dispatch = jest.fn();
        const wrapper = ({ children }: PropsWithChildren) => (
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                <PageContext.Provider value={{ module: "test_module" }}>{children}</PageContext.Provider>
            </TaipyContext.Provider>
        );

        const { result } = renderHook(() => useActions(), { wrapper });

        act(() => {
            result.current.sendAction("test_action_name", "test_function_name");
        });

        expect(dispatch).toHaveBeenCalledWith({
            type: "SEND_ACTION_ACTION",
            name: "test_action_name",
            context: "test_module",
            payload: { action: "test_function_name", args: [] },
        });
    });

    it("dispatches an Action action with arguments", () => {
        const dispatch = jest.fn();
        const wrapper = ({ children }: PropsWithChildren) => (
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                <PageContext.Provider value={{ module: "test_module" }}>{children}</PageContext.Provider>
            </TaipyContext.Provider>
        );

        const { result } = renderHook(() => useActions(), { wrapper });

        act(() => {
            result.current.sendAction("test_action_name", "test_function_name", "test text", 42);
        });

        expect(dispatch).toHaveBeenCalledWith({
            type: "SEND_ACTION_ACTION",
            name: "test_action_name",
            context: "test_module",
            payload: { action: "test_function_name", args: ["test text", 42] },
        });
    });

    it("dispatches a SendUpdate action", () => {
        const dispatch = jest.fn();
        const wrapper = ({ children }: PropsWithChildren) => (
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                <PageContext.Provider value={{ module: "test_module" }}>{children}</PageContext.Provider>
            </TaipyContext.Provider>
        );

        const { result } = renderHook(() => useActions(), { wrapper });

        act(() => {
            result.current.sendUpdate("test_var_name", 12345, "test_on_change", false, "rel_test_var_name");
        });

        expect(dispatch).toHaveBeenCalledWith({
            type: "SEND_UPDATE_ACTION",
            name: "test_var_name",
            context: "test_module",
            propagate: false,
            payload: { value: 12345, on_change: "test_on_change", relvar: "rel_test_var_name" },
        });
    });
});

describe("useRequestUpdateOnFirstRender", () => {
    it("dispatches a RequestUpdate action on first render", () => {
        const dispatch = jest.fn();
        const wrapper = ({ children }: PropsWithChildren) => (
            <TaipyContext.Provider value={{ state: INITIAL_STATE, dispatch }}>
                <PageContext.Provider value={{ module: "test_module" }}>{children}</PageContext.Provider>
            </TaipyContext.Provider>
        );

        renderHook(() => useRequestUpdateOnFirstRender("test_id", "first=var_a;second=var_b", "var_c", true), {
            wrapper,
        });

        expect(dispatch).toHaveBeenCalledTimes(1);
        expect(dispatch).toHaveBeenCalledWith({
            type: "REQUEST_UPDATE",
            name: "",
            context: "test_module",
            payload: {
                id: "test_id",
                names: ["var_a", "var_b", "var_c"],
                refresh: true,
            },
        });
    });
});
