import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";

import mediaQuery from "css-mediaquery";
import { ThemeProvider, createTheme } from "@mui/material/styles";

import Layout from './Layout';

describe("Layout Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Layout><div>bar</div></Layout>);
        const elt = getByText("bar");
        expect(elt.parentElement?.tagName).toBe("DIV");
        expect(elt.parentElement).toHaveStyle({display: 'grid'})
    })
    it("displays the right info for string", async () => {
        const {getByText} = render(<Layout className="taipy-layout"><div>bar</div></Layout>);
        const elt = getByText("bar");
        expect(elt.parentElement).toHaveClass("taipy-layout");
    })
    it("displays the default value", async () => {
        const {getByText} = render(<Layout gap="1rem" columns="1 1 1 1" ><div>foo</div></Layout>);
        const elt = getByText("foo");
        expect(elt.parentElement).toHaveStyle({"grid-template-columns": "1fr 1fr 1fr 1fr"})
    })
    it("keeps the grid definition", async () => {
        const {getByText} = render(<Layout gap="1rem" columns="10px 1em 1rem 1fr" ><div>foo</div></Layout>);
        const elt = getByText("foo");
        expect(elt.parentElement).toHaveStyle({"grid-template-columns": "10px 1em 1rem 1fr"})
    })
    it("handles the concise column expression", async () => {
        const {getByText} = render(<Layout gap="1rem" columns="1*3px 1 3*1em 2 3 3*2" ><div>foo</div></Layout>);
        const elt = getByText("foo");
        expect(elt.parentElement).toHaveStyle({"grid-template-columns": "3px 1fr 1em 1em 1em 2fr 3fr 2fr 2fr 2fr"})
    })
    it("displays the default value for mobile", async () => {
        Object.defineProperty(window, "matchMedia", {
            writable: true,
            value: jest.fn().mockImplementation(query => ({
              matches: mediaQuery.match(query, {
                width: 10,
              }),
              media: query,
              onchange: null,
              addListener: jest.fn(), // Deprecated
              removeListener: jest.fn(), // Deprecated
              addEventListener: jest.fn(),
              removeEventListener: jest.fn(),
              dispatchEvent: jest.fn(),
            })),});
        const {getByText} = render(<ThemeProvider theme={createTheme()}><Layout gap="1rem" columns="1 1 1 1" ><div>foo</div></Layout></ThemeProvider>);
        const elt = getByText("foo");
        expect(elt.parentElement).toHaveStyle({"grid-template-columns": "1fr"});
    })
});
