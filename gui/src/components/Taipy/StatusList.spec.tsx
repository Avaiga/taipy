import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import { StatusType } from "./Status";
import StatusList from './StatusList';

const statuses: StatusType[] = [
    {status: "info", message: "info"},
    {status: "error", message: "error"},
    {status: "warning", message: "warning"},
    {status: "success", message: "success"},
];

describe("StatusList Component", () => {
    it("renders", async () => {
        const {getByText} = render(<StatusList value={statuses} />);
        const elt = getByText("4 statuses");
        const av = getByText("E");
        expect(elt.tagName).toBe("SPAN");
        expect(av.tagName).toBe("DIV");
    })
    it("uses the class", async () => {
        const {getByText} = render(<StatusList value={statuses} className="taipy-status" />);
        const elt = getByText("4 statuses");
        expect(elt.parentElement).toHaveClass("taipy-status");
    })
    it("can be opened when more than 1 status", async () => {
        const {getByTestId} = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
    })
    it("cannot be opened when 1 status", async () => {
        const {queryAllByRole} = render(<StatusList value={statuses[0]} />);
        expect(queryAllByRole("button")).toHaveLength(0);
    })
    it("displays a default status", async () => {
        const {getByText} = render(<StatusList value={[]}  />);
        getByText("No Status");
        getByText("I");
    })
    it("opens on click", async () => {
        const {getByTestId, getByText} = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        userEvent.click(elt);
        const selt = getByText("info");
        expect(selt.parentElement?.parentElement?.childElementCount).toBe(4);
    })
    it("hide closed statuses", async () => {
        const {getByTestId, queryAllByTestId} = render(<StatusList value={statuses} />);
        const elt = getByTestId("ArrowDownwardIcon");
        userEvent.click(elt);
        const icons = queryAllByTestId("CancelIcon");
        expect(icons).toHaveLength(4);
        userEvent.click(icons[0]);
        expect(queryAllByTestId("CancelIcon")).toHaveLength(3);
    })
});
