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
import { LoVElt } from "./lovUtils";

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
    it("holds a numeric range", async () => {
        const { getByDisplayValue } = render(
            <Slider defaultValue={"[10,90]"} value={undefined as unknown as number[]} />
        );
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
        expect(elts[0].tagName).toBe("P");
        expect(elts[1].tagName).toBe("P");
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
        const { getByDisplayValue } = render(
            <Slider value={["B", "C"]} defaultLov={'[["A", "A"], ["B", "B"], ["C", "C"], ["D", "D"]]'} />
        );
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
    it("calls props.onChange when update is true and changeDelay is set", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;

        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={33} changeDelay={100} />
            </TaipyContext.Provider>
        );

        const slider = getByRole("slider");
        fireEvent.change(slider, { target: { value: 50 } });

        // Wait for the changeDelay timeout
        await new Promise((r) => setTimeout(r, 150));

        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: 50 },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("should handle change when continuous is set to true", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const lovArray: [string, string][] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const { getByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={33} continuous={false} lov={lovArray} />
            </TaipyContext.Provider>
        );

        const slider = getByRole("slider");
        fireEvent.change(slider, { target: { value: 50 } });

        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: "Item 3" },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("returns correct text when before is true and textAnchor is top", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;

        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const { container } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider changeDelay={0} lov={lovList} textAnchor="top" />
            </TaipyContext.Provider>
        );
        expect(container).toHaveTextContent("Description 1");
    });
    it("handles case when idx is -1", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;

        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const labels = {
            "Item 4": "Label for Item 4", // This will cause idx to be -1
        };

        const { container } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider changeDelay={0} lov={lovList} labels={JSON.stringify(labels)} />
            </TaipyContext.Provider>
        );

        // Check that the label for "Item 4" is not found
        expect(container).not.toHaveTextContent("Label for Item 4");
    });
    it("returns correct style for textAnchor 'left'", () => {
        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const { container } = render(<Slider lov={lovList} textAnchor="left" />);
        const slider = container.querySelector("div");
        expect(slider).toBeInTheDocument();
    });
    it("should parse lov when default value is greater than 2 values", async () => {
        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const { container } = render(<Slider defaultValue='["Item 2", "Item 3"]' lov={lovList} />);
        const slider = container.querySelector("div");
        expect(slider).toBeInTheDocument();
    });
    it("should parse lov when default value is less than 2 values", async () => {
        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const { container } = render(<Slider defaultValue='["Item 3"]' lov={lovList} />);
        const slider = container.querySelector("div");
        expect(slider).toBeInTheDocument();
    });
    it("throws an error when defaultValue is an invalid JSON string", () => {
        const lovList: LoVElt[] = [
            ["Item 1", "Description 1"],
            ["Item 2", "Description 2"],
            ["Item 3", "Description 3"],
        ];

        const errorSpy = jest.spyOn(global, "Error");

        expect(() => {
            render(<Slider defaultValue="invalid-json" lov={lovList} />);
        }).toThrow("Slider lov value couldn't be parsed");

        expect(errorSpy).toHaveBeenCalledWith("Slider lov value couldn't be parsed");

        errorSpy.mockRestore();
    });
    it("throws an error when defaultValue contains non-numeric values", () => {
        const errorSpy = jest.spyOn(global, "Error");
        render(<Slider defaultValue='["Item 1", "Item 2"]' />);
        expect(errorSpy).toHaveBeenCalledWith("Slider values should all be numbers");
    });
    it("should return number when default value is a number", async () => {
        const { container } = render(<Slider defaultValue={1} />);
        const slider = container.querySelector("div");
        expect(slider).toBeInTheDocument();
    });
    it("should return number when default value is a number", async () => {
        const { getByRole } = render(<Slider defaultValue={"10"} />);
        const inputElement = getByRole("slider", { hidden: true }) as HTMLInputElement;
        expect(inputElement).toHaveValue("10");
    });
    it("should return an array numbers when value is an array of number", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const lovList: LoVElt[] = [
            ["1", "Description 1"],
            ["2", "Description 2"],
            ["3", "Description 3"],
        ];

        const { getAllByRole } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Slider value={["1", "2"]} lov={lovList} />
            </TaipyContext.Provider>
        );

        const sliders = getAllByRole("slider");
        fireEvent.change(sliders[0], { target: { value: "2" } });

        expect(dispatch).toHaveBeenCalledWith({
            name: "",
            payload: { value: ["2", "3"] },
            propagate: true,
            type: "SEND_UPDATE_ACTION",
        });
    });
    it("should change the orientation of the slider to horizontal", async () => {
        render(<Slider value={5} orientation="horizontal" />);
        const horizontalInputs = document.querySelectorAll('input[aria-orientation="horizontal"]');
        expect(horizontalInputs).toHaveLength(1);
    });
    it("should change the orientation of the slider to vertical", async () => {
        render(<Slider value={5} orientation="vertical" />);
        const verticalInputs = document.querySelectorAll('input[aria-orientation="vertical"]');
        expect(verticalInputs).toHaveLength(1);
    });
    it("should change the orientation of the slider to vertical when default value is an array", async () => {
        render(<Slider orientation="vertical" defaultValue={[1, 2]} />);
        const verticalInputs = document.querySelectorAll('input[aria-orientation="vertical"]');
        expect(verticalInputs).toHaveLength(2);
    });
    it("should return an array of number when value is an array of number and no lov is defined", async () => {
        const { getAllByRole } = render(<Slider value={[1, 2]} />);
        const sliders = getAllByRole("slider");
        expect(sliders).toHaveLength(2);
    });
});
