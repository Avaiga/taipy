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
import userEvent from "@testing-library/user-event";

import { StatusType } from "./Status";
import StatusList from "./StatusList";

const statuses = [
    { status: "info", message: "info" },
    ["error", "error"],
    { status: "warning", message: "warning" },
    { status: "success", message: "success" },
] as Array<[string, string] | StatusType>;

describe("StatusList Component", () => {
    it("renders", async () => {
        const { getByText } = render(<StatusList value={statuses} />);
        const elt = getByText("4 statuses");
        expect(elt.tagName).toBe("SPAN");
    });
    it("uses the class", async () => {
        const { getByText } = render(<StatusList value={statuses} className="taipy-status" />);
        const elt = getByText("4 statuses");
        expect(elt.parentElement).toHaveClass("taipy-status");
    });
    it("can be opened when more than 1 status", async () => {
        const { getByTestId } = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
    });
    it("cannot be opened when 1 status", async () => {
        const { queryAllByRole } = render(<StatusList value={statuses[0]} />);
        expect(queryAllByRole("button")).toHaveLength(0);
    });
    it("displays a default status", async () => {
        const { getByText } = render(<StatusList value={[]} />);
        getByText("No Status");
    });
    it("opens on click", async () => {
        const { getByTestId, getByText } = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        await userEvent.click(elt);
        const selt = getByText("info");
        expect(selt.parentElement?.parentElement?.childElementCount).toBe(4);
    });
    it("hide closed statuses", async () => {
        const { getByTestId, queryAllByTestId } = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        await userEvent.click(elt);
        const icons = queryAllByTestId("CancelIcon");
        expect(icons).toHaveLength(4);
        await userEvent.click(icons[0]);
        expect(queryAllByTestId("CancelIcon")).toHaveLength(3);
    });
});
