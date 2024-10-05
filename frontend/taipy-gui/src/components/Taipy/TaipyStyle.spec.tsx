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

import { HelmetProvider } from "react-helmet-async";
import TaipyStyle, { getStyle } from "./TaipyStyle";
import Button from "./Button";

const style = { td: { color: "blue" } };

describe("TaipyStyle Component", () => {
    it("renders", async () => {
        render(
            <HelmetProvider>
                <TaipyStyle className="test" content={JSON.stringify(style)} />
            </HelmetProvider>
        );
        await waitFor(() => expect(document.querySelector("style")).toBeInTheDocument());
        const elt = document.querySelector("style");
        expect(elt).toHaveTextContent(".test{td{color:blue}}")
    });

    it("get the class", async () => {
        const { getByRole } = render(
            <HelmetProvider>
                <Button label="test">
                    <TaipyStyle className="test" content={JSON.stringify(style)} />
                </Button>
            </HelmetProvider>
        );
        expect(getByRole("button")).toHaveClass("test");
    });
    it("get the style", () => {
        expect(getStyle({cls: {a: "b"}})).toBe("cls{a:b}");
        expect(getStyle({cls: {a: "b", subCls: {c: "d"}}})).toBe("cls{a:b;subCls{c:d}}");
        expect(getStyle({cls: {a: [1, 2], subCls: {c: "d"}, e: 1, f: undefined}})).toBe("cls{a:1,2;subCls{c:d};e:1;f:undefined}");
        expect(getStyle({cls: {a: "b", subCls: {c: "d", ssCls: {e: "f"}}}})).toBe("cls{a:b;subCls{c:d;ssCls{e:f}}}");
    });
});
