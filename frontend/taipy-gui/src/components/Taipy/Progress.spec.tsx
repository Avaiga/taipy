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

import { render } from "@testing-library/react";
import "@testing-library/jest-dom";

import Progress from "./Progress";

describe("Progress component", () => {
    it("renders circular progress without value (indeterminate)", () => {
        const { getByRole } = render(<Progress />);
        const elt = getByRole("progressbar");
        expect(elt).toHaveClass("MuiCircularProgress-root");
    });
    it("uses the class", async () => {
        const { getByRole } = render(<Progress className="taipy-progress" />);
        const elt = getByRole("progressbar");
        expect(elt).toHaveClass("taipy-progress");
    });
    it("renders circular progress with value (determinate)", () => {
        const { getByRole, getByText } = render(<Progress showValue value={50} />);
        const elt = getByRole("progressbar");
        const valueText = getByText("50%");
        expect(elt).toHaveClass("MuiCircularProgress-root");
        expect(valueText).toBeInTheDocument();
    });
    it("renders linear progress without value (inderminate)", () => {
        const { getByRole } = render(<Progress linear />);
        const elt = getByRole("progressbar");
        expect(elt).toHaveClass("MuiLinearProgress-root");
    });
    it("renders linear progress with value (determinate)", () => {
        const { getByRole, getByText } = render(<Progress linear showValue value={50} />);
        const elt = getByRole("progressbar");
        const valueText = getByText("50%");
        expect(elt).toHaveClass("MuiLinearProgress-root");
        expect(valueText).toBeInTheDocument();
    });
});
