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
    it("shows discrete value when lov", async () => {
        const { getAllByText } = render(
            <Slider
                value={"Item 1"}
                defaultLov={'[["Item 1", "Item 1"], ["Item 2", "Item 2"], ["Item 3", "Item 3"]]'}
            />
        );
        const elts = getAllByText("Item 1");
        expect(elts).toHaveLength(2);
        const tags = elts.map(elt => elt.tagName)
        expect(tags).toContain("P")
        expect(tags).toContain("P")
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
