import React from "react";
import {render, fireEvent, waitFor, screen} from "@testing-library/react";
import "@testing-library/jest-dom";

import { ENDPOINT } from "../../utils";
import Field from './Field';

describe("Field Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Field value="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("SPAN");
    })
    it("displays the right info for string", async () => {
        const {getByText} = render(<Field value="toto" defaultValue="titi" className="taipy-field" />);
        const elt = getByText("toto");
        expect(elt.classList).toContain("taipy-field");
    })
    it("displays the default value", async () => {
        const {getByText} = render(<Field defaultValue="titi" value={undefined as unknown as string} />);
        getByText("titi");
    })
    it("displays a date with format", async () => {
        const myDate = new Date();
        myDate.setMonth(1, 1);
        const {getByText} = render(<Field defaultValue="titi" value={myDate.toISOString()} dataType="datetime.datetime" format="MM/dd" /> );
        const elt = getByText("02/01");
    })
    it("displays a number with format", async () => {
        const {getByText} = render(<Field defaultValue="titi" value={12} dataType="int" format="%.2f" /> );
        const elt = getByText("12.00");
    })
});
