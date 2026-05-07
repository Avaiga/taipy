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
import { createContext } from "react";

import ScenarioSelector from "./ScenarioSelector";
import { getEmptyScenario } from "./ScenarioSelector";
import { useDispatchRequestUpdateOnFirstRender } from "taipy-gui";

const TaipyContext = createContext<object>({ state: {}, dispatch: () => null });

describe("ScenarioSelector Component", () => {
    it("renders", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
            />
        );
        const elt = getByText("Add scenario");
        expect(elt.tagName).toBe("BUTTON");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
                className="test"
            />
        );
        const elt = getByText("Add scenario");
        expect(elt.closest(".MuiBox-root")).toHaveClass("test");
    });
    it("is disabled", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
                active={false}
            />
        );
        const elt = getByText("Add scenario");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
            />
        );
        const elt = getByText("Add scenario");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
                active={true}
            />
        );
        const elt = getByText("Add scenario");
        expect(elt).not.toBeDisabled();
    });
    it("dispatch a message at first render", async () => {
        const dispatch = jest.fn();
        const state = {};
        render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <ScenarioSelector
                    onScenarioCrud="onScenarioCrud"
                    onScenarioSelect="onScenarioSelect"
                    height="50vh"
                    updateVars=""
                />
            </TaipyContext.Provider>
        );
        await waitFor(() => expect(useDispatchRequestUpdateOnFirstRender).toHaveBeenCalled());
    });
    it("disables add scenario when reason", async () => {
        const { getByText } = render(
            <ScenarioSelector
                onScenarioCrud="onScenarioCrud"
                onScenarioSelect="onScenarioSelect"
                height="50vh"
                updateVars=""
                creationNotAllowed="Because"
            />
        );
        const elt = getByText("Add scenario");
        expect(elt).toBeDisabled();
    });
});

describe("getEmptyScenario", () => {
    it("returns a fresh date on each call", async () => {
        const first = getEmptyScenario();
        // Wait a small amount to ensure timestamps differ
        await new Promise((resolve) => setTimeout(resolve, 10));
        const second = getEmptyScenario();

        expect(first.date).not.toBe(second.date);
        expect(new Date(second.date).getTime()).toBeGreaterThan(new Date(first.date).getTime());
    });

    it("returns default empty values", () => {
        const scenario = getEmptyScenario();

        expect(scenario.config).toBe("");
        expect(scenario.name).toBe("");
        expect(scenario.properties).toEqual([]);
        expect(scenario.date).toBeTruthy();
        // Verify date is a valid ISO string
        expect(new Date(scenario.date).toISOString()).toBe(scenario.date);
    });
});
