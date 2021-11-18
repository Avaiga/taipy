import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";

import Part from './Part';

describe("Part Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Part>bar</Part>);
        const elt = getByText("bar");
        expect(elt.tagName).toBe("DIV");
        expect(elt).toHaveClass("MuiBox-root")
    })
    it("displays the right info for string", async () => {
        const {getByText} = render(<Part className="taipy-part">bar</Part>);
        const elt = getByText("bar");
        expect(elt).toHaveClass("taipy-part");
    })
});
