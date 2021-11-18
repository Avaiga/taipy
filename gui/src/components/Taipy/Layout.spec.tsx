import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";

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
        const {getByText} = render(<Layout gap="1rem" type="1 1 1 1" ><div>foo</div></Layout>);
        const elt = getByText("foo");
        expect(elt.parentElement).toHaveStyle({"grid-template-columns": "25% calc(25% - 1rem) calc(25% - 1rem) calc(25% - 1rem)"})
    })
});
