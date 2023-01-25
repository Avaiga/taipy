/*
 * Copyright 2023 Avaiga Private Limited
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

import Indicator from './Indicator';

describe("Indicator Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Indicator defaultDisplay="Display" defaultValue={12} />);
        const elt = getByText("Display");
        expect(elt.tagName).toBe("SPAN");
    })
    it("displays the right info for string", async () => {
        const {getByText} = render(<Indicator value={12} defaultValue={12} defaultDisplay="Display" className="taipy-indicator" />);
        const elt = getByText("Display");
        const thumb = elt.closest(".MuiSlider-thumb");
        expect(thumb).toHaveStyle({left: "12%"});
    })
    it("displays the default value", async () => {
        const {getByText} = render(<Indicator defaultDisplay="Display" display={undefined as unknown as string} defaultValue={12} />);
        getByText("Display");
    })
    it("displays min and max", async () => {
        const {getByText} = render(<Indicator defaultDisplay="Display" display={undefined as unknown as string} defaultValue={12} min={-12} max={25} />);
        getByText("-12");
        getByText("25");
    })
    it("displays with format", async () => {
        const myDate = new Date();
        myDate.setMonth(1, 1);
        const {getByText} = render(<Indicator defaultDisplay={10} format="%.3f" defaultValue={20} /> );
        const elt = getByText("10.000");
    })
});
