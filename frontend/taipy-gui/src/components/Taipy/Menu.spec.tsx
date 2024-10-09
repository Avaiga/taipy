import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { BrowserRouter as Router } from "react-router-dom";

import Menu from "./Menu";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";
import { LovItem } from "../../utils/lov";

const lov: LovItem[] = [
    { id: "id1", item: "Item 1" },
    { id: "id2", item: "Item 2" },
    { id: "id3", item: "Item 3" },
    { id: "id4", item: "Item 4" },
];

const imageItem: LovItem = { id: "ii1", item: { path: "/img/fred.png", text: "Image" } };

describe("Menu Component", () => {
    it("renders", async () => {
        const { getByText } = render(
            <Router>
                <Menu lov={lov} />
            </Router>
        );
        const elt = getByText("Item 1");
        expect(elt.tagName).toBe("SPAN");
    });

    it("uses the class", async () => {
        const { getByText } = render(
            <Router>
                <Menu lov={lov} className="taipy-menu" />
            </Router>
        );
        const elt = getByText("Item 1");
        expect(elt.closest(".taipy-menu")).not.toBeNull();
    });

    it("can display an avatar with initials", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByText } = render(
            <Router>
                <Menu lov={lovWithImage} />
            </Router>
        );
        const elt = getByText("I2");
        expect(elt.tagName).toBe("DIV");
    });

    it("can display an image", async () => {
        const lovWithImage = [...lov, imageItem];
        const { getByAltText } = render(
            <Router>
                <Menu lov={lovWithImage} />
            </Router>
        );
        const elt = getByAltText("Image");
        expect(elt.tagName).toBe("IMG");
    });

    it("is disabled", async () => {
        const { getAllByRole } = render(
            <Router>
                <Menu lov={lov} active={false} />
            </Router>
        );
        const elts = getAllByRole("button");
        elts.forEach((elt, idx) => idx > 0 && expect(elt).toHaveClass("Mui-disabled"));
    });

    it("is enabled by default", async () => {
        const { getAllByRole } = render(
            <Router>
                <Menu lov={lov} />
            </Router>
        );
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });

    it("is enabled by active", async () => {
        const { getAllByRole } = render(
            <Router>
                <Menu lov={lov} active={true} />
            </Router>
        );
        const elts = getAllByRole("button");
        elts.forEach((elt) => expect(elt).not.toHaveClass("Mui-disabled"));
    });

    it("can disable a specific item", async () => {
        const { getByText } = render(
            <Router>
                <Menu lov={lov} inactiveIds={[lov[0].id]} />
            </Router>
        );
        const elt = getByText(lov[0].item as string);
        const button = elt.closest('[role="button"]');
        expect(button).toHaveClass("Mui-disabled");
    });

    it("dispatch a well formed message", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText } = render(
            <Router>
                <TaipyContext.Provider value={{ state, dispatch }}>
                    <Menu lov={lov} onAction="action" />
                </TaipyContext.Provider>
            </Router>
        );
        const elt = getByText(lov[0].item as string);
        await userEvent.click(elt);
        expect(dispatch).toHaveBeenCalledWith({
            name: "menu",
            payload: { action: "action", args: [lov[0].id] },
            type: "SEND_ACTION_ACTION",
        });
    });
});
