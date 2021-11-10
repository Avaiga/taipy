import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";

import Link from "./Link";
import { INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

describe("Link Component", () => {
    const dispatch = jest.fn();
    it("renders as an external link", async () => {
        const state: TaipyState = { ...INITIAL_STATE, locations: { } };
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <Link href="toto">toto</Link>
            </TaipyContext.Provider>
        );
        const elt = getByText("toto");
        expect(elt.tagName).toBe("A");
    });
    it("renders as a router link", async () => {
        const state: TaipyState = { ...INITIAL_STATE, locations: { toto: "toto" } };
        const { getByText } = render(
            <TaipyContext.Provider value={{ state, dispatch }}>
                <BrowserRouter>
                    <Link href="toto">toto</Link>
                </BrowserRouter>
            </TaipyContext.Provider>
        );
        const elt = getByText("toto");
        expect(elt.tagName).toBe("A");
    });
});
