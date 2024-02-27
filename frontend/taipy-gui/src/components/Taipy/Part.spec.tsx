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
    it("renders an iframe", async () => {
        const {getByText} = render(<Part className="taipy-part" page="http://taipy.io">bar</Part>);
        const elt = getByText("bar");
        expect(elt.parentElement?.firstElementChild?.tagName).toBe("DIV");
        expect(elt.parentElement?.firstElementChild?.firstElementChild?.tagName).toBe("IFRAME");
    })
});
