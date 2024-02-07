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
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

import Slider from "./Slider";
import { TaipyContext } from "../../context/taipyContext";
import { TaipyState, INITIAL_STATE } from "../../context/taipyReducers";

describe("Slider Component", () => {
    it("renders", async () => {
        const { getByDisplayValue } = render(<Slider value={12} />);
        const elt = getByDisplayValue("12");
        expect(elt.tagName).toBe("INPUT");
    });
    it("displays the right info for string", async () => {
        const { getByDisplayValue } = render(<Slider value={12} defaultValue={1} className="taipy-slider" />);
        const elt = getByDisplayValue(12);
        expect(elt.parentElement?.parentElement?.parentElement).toHaveClass("taipy-slider");
    });
    it("displays the default value", async () => {
        const { getByDisplayValue } = render(<Slider defaultValue={1} value={undefined as unknown as number} />);
        getByDisplayValue("1");
    });
    it("is disabled", async () => {
        const { getByDisplayValue } = render(<Slider value={33} active={false} />);
        const elt = getByDisplayValue("33");
        expect(elt).toBeDisabled();
    });
    it("is enabled by default", async () => {
        const { getByDisplayValue } = render(<Slider value={33} />);
        const elt = getByDisplayValue("33");
        expect(elt).not.toBeDisabled();
    });
    it("is enabled by active", async () => {
        const { getByDisplayValue } = render(<Slider value={33} active={true} />);
        const elt = getByDisplayValue("33");
        expect(elt).not.toBeDisabled();
    });
    it("is limited by min & max", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={33} min={1} max={50} />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("33") as HTMLInputElement;
        fireEvent.change(elt, { target: { value: 99 } });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 50 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });

        fireEvent.change(elt, { target: { value: 0 } });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 1 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });

        fireEvent.change(elt, { target: { value: 30 } });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 30 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("changes by set step", async()=>{
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={33} min={1} max={50} step={0.1} />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("33") as HTMLInputElement;
        const step = parseFloat(elt.step);
        fireEvent.change(elt, {target:{value: 33 + step }});
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 33.1 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });

        fireEvent.change(elt, { target: { value: 2 } });
        fireEvent.change(elt, { target:{ value: 2 - step }});
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 1.9 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    })
    it("holds a numeric range", async () => {
        const { getByDisplayValue } = render(<Slider defaultValue={"[10,90]"} value={undefined as unknown as number[]} />);
        const elt1 = getByDisplayValue("10");
        expect(elt1.tagName).toBe("INPUT");
        const elt2 = getByDisplayValue("90");
        expect(elt2.tagName).toBe("INPUT");
    });
    it("shows discrete value when lov", async () => {
        const { getAllByText } = render(
            <Slider
                value={"Item 1"}
                defaultLov={'[["Item 1", "Item 1"], ["Item 2", "Item 2"], ["Item 3", "Item 3"]]'}
                labels={true}
            />
        );
        const elts = getAllByText("Item 1");
        expect(elts).toHaveLength(3);
        expect(elts[0].tagName).toBe("P")
        expect(elts[1].tagName).toBe("P")
    });
    it("doesn't show text when_text_anchor is none", async () => {
        const { getAllByText } = render(
            <Slider
                value={"Item 1"}
                defaultLov={'[["Item 1", "Item 1"], ["Item 2", "Item 2"], ["Item 3", "Item 3"]]'}
                textAnchor="none"
            />
        );
        const elts = getAllByText("Item 1");
        expect(elts).toHaveLength(1);
        expect(elts[0].tagName).toBe("P");
    });
    it("holds a lov range", async () => {
        const { getByDisplayValue } = render(<Slider value={["B", "C"]} defaultLov={'[["A", "A"], ["B", "B"], ["C", "C"], ["D", "D"]]'} />);
        const elt1 = getByDisplayValue("1");
        expect(elt1.tagName).toBe("INPUT");
        const elt2 = getByDisplayValue("2");
        expect(elt2.tagName).toBe("INPUT");
    });
    it("shows marks", async () => {
        const { getAllByText } = render(
            <Slider
                value={"Item 1"}
                defaultLov={'[["Item 1", "Item 1"], ["Item 2", "Item 2"], ["Item 3", "Item 3"]]'}
                labels={'{"Item 1":"Item 1"}'}
            />
        );
        const elts = getAllByText("Item 1");
        expect(elts).toHaveLength(3);
        expect(elts[0].tagName).toBe("SPAN");
    });
    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByDisplayValue } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={33} />
            </TaipyContext.Provider>
        );
        const elt = getByDisplayValue("33");
        fireEvent.change(elt, { target: { value: 99 } });
        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 99 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
});
