/*
 * Copyright 2021-2025 Avaiga Private Limited
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
import StatusList, { getStatusStrValue, getStatusIntValue } from "./StatusList";

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
        const av = getByText("E");
        expect(elt.tagName).toBe("SPAN");
        expect(av.tagName).toBe("DIV");
    });
    it("uses the class", async () => {
        const { getByText } = render(<StatusList value={statuses} className="taipy-status" />);
        const elt = getByText("4 statuses");
        expect(elt.parentElement?.parentElement).toHaveClass("taipy-status");
    });
    it("can be opened when more than 1 status", async () => {
        const { getByTestId } = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        expect(elt).toBeInTheDocument();
    });
    it("cannot be opened when 1 status", async () => {
        const { queryAllByRole } = render(<StatusList value={statuses[0]} />);
        expect(queryAllByRole("button")).toHaveLength(0);
    });
    it("displays a default status", async () => {
        const { getByText } = render(<StatusList value={[]} />);
        getByText("No Status");
        getByText("I");
    });
    it("opens on click", async () => {
        const { getByTestId, getByText } = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        await userEvent.click(elt);
        const infoElt = getByText("info");
        expect(infoElt.parentElement?.parentElement?.childElementCount).toBe(4);
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
    it("should return -1 for unknown status", () => {
        expect(getStatusIntValue("unknown")).toBe(-1);
        expect(getStatusIntValue("")).toBe(-1);
        expect(getStatusIntValue("a")).toBe(-1);
        expect(getStatusIntValue("z")).toBe(-1);
    });
    it('should return "info" for status 0', () => {
        expect(getStatusStrValue(0)).toBe("info");
    });

    it('should return "success" for status 1', () => {
        expect(getStatusStrValue(1)).toBe("success");
    });

    it('should return "warning" for status 2', () => {
        expect(getStatusStrValue(2)).toBe("warning");
    });

    it('should return "error" for status 3', () => {
        expect(getStatusStrValue(3)).toBe("error");
    });

    it('should return "unknown" for any other status', () => {
        expect(getStatusStrValue(0)).toBe("info");
        expect(getStatusStrValue(5)).toBe("unknown");
        expect(getStatusStrValue(-1)).toBe("unknown");
    });
    it("should handle invalid JSON in defaultValue", () => {
        const invalidDefaultValue = "{invalidJson}";
        const consoleSpy = jest.spyOn(console, "info").mockImplementation(() => {});
        const { getByText } = render(<StatusList value={undefined!} defaultValue={invalidDefaultValue} />);
        expect(consoleSpy).toHaveBeenCalledWith(
            expect.stringContaining("Cannot parse status value"),
            expect.any(SyntaxError),
        );
        const elt = getByText("No Status");
        expect(elt).toBeInTheDocument();
        consoleSpy.mockRestore();
    });
    it("renders default content when content is not provided", () => {
        const statuses = [
            { status: "info", message: "Information" },
            { status: "warning", message: "Warning" },
        ];

        const { getByText } = render(<StatusList value={statuses} />);
        getByText("W");
    });
    it("renders custom content passed via 'customIcon' prop", () => {
        const statuses = [
            { status: "info", message: "Information" },
            { status: "warning", message: "Warning" },
        ];

        const content =
            "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'><circle cx='8' cy='8' r='8' fill='red'/></svg>";

        const { container } = render(
            <StatusList value={statuses} useIcon={JSON.stringify({ warning: content, info: true })} />,
        );

        // Check if the SVG is rendered for the warning status
        const svg = container.querySelector("svg");
        expect(svg).toBeInTheDocument();
    });
});
