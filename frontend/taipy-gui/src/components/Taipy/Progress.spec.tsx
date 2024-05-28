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

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import Progress from "./Progress";

describe("Progress component", () => {
    it("renders", async () => {
        render(<Progress />);
        const progressElement = screen.getByRole("progressbar");
        expect(progressElement).toBeInTheDocument();
    });
    it("renders circular element by default", () => {
        render(<Progress />);
        const progressElement = screen.getByRole("progressbar");
        expect(progressElement).toBeInTheDocument();
    });
    it("renders a linear element on providing the parameter `linear`", () => {
        render(<Progress linear={true} />);
        const progressElement = screen.getByRole("progressbar");
        expect(progressElement).toBeInTheDocument();
    });
    it("renders a circular element on providing the parameters `showValues` and `value`", () => {
        const { getByDisplayValue } = render(<Progress showValue={true} value={50} />);
        getByDisplayValue("50");
    });
    it("renders a linear element on providing the parameters `linear`, `showValue` and `value`", () => {
        const { getByDisplayValue } = render(<Progress showValue={true} value={50} linear={true} />);
        getByDisplayValue("50");
    });
});
