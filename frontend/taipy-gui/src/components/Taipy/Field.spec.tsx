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
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

import Field from "./Field";

describe("Field Component", () => {
    it("renders", async () => {
        const { getByText } = render(<Field value="toto" />);
        const elt = getByText("toto");
        expect(elt.tagName).toBe("SPAN");
    });
    it("displays the right info for string", async () => {
        const { getByText } = render(<Field value="toto" defaultValue="titi" className="taipy-field" />);
        const elt = getByText("toto");
        expect(elt).toHaveClass("taipy-field");
    });
    it("displays the default value", async () => {
        const { getByText } = render(<Field defaultValue="titi" value={undefined as unknown as string} />);
        getByText("titi");
    });
    it("displays a date with format", async () => {
        const myDate = new Date();
        myDate.setMonth(1, 1);
        const { getByText } = render(
            <Field defaultValue="titi" value={myDate.toISOString()} dataType="datetime" format="MM/dd" />
        );
        getByText("02/01");
    });
    it("displays a int with format", async () => {
        const { getByText } = render(<Field defaultValue="titi" value={12} dataType="int" format="%.2f" />);
        getByText("12.00");
    });
    it("displays a float with format", async () => {
        const { getByText } = render(
            <Field defaultValue="titi" value={12.1} dataType="float" format="float is %.0f" />
        );
        getByText("float is 12");
    });
    it("displays with width=70%", async () => {
        const { getByText } = render(<Field value="titi" width="70%" />);
        const elt = getByText("titi");
        expect(elt).toHaveStyle("width: 70%");
    });
    it("displays with width=500", async () => {
        const { getByText } = render(<Field value="titi" width={500} />);
        const elt = getByText("titi");
        expect(elt).toHaveStyle("width: 500px");
    });
    it("can render markdown", async () => {
        render(<Field value="titi" className="taipy-text" mode="md" />);
        const elt = document.querySelector(".taipy-text");
        await waitFor(() => expect(elt?.querySelector("p")).not.toBeNull());
    });
    it("can render pre", async () => {
        render(<Field value="titi" className="taipy-text" mode="pre" />);
        const elt = document.querySelector("pre.taipy-text");
        expect(elt).toBeInTheDocument();
    });
});
