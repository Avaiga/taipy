import React from "react";
import {render} from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

import { PlusOneOutlined } from "@mui/icons-material";

import Status, { StatusType } from './Status';

const status: StatusType = {status: "status", message: "message"};

describe("Status Component", () => {
    it("renders", async () => {
        const {getByText} = render(<Status value={status} />);
        const elt = getByText("message");
        const av = getByText("S");
        expect(elt.tagName).toBe("SPAN");
        expect(av.tagName).toBe("DIV");
    })
    it("uses the class", async () => {
        const {getByText} = render(<Status value={status} className="taipy-status" />);
        const elt = getByText("message");
        expect(elt.parentElement).toHaveClass("taipy-status");
    })
    it("can be closed", async () => {
        const myClose = jest.fn();
        const {getByTestId} = render(<Status value={status} onClose={myClose} />);
        const elt = getByTestId("CancelIcon");
        userEvent.click(elt);
        expect(myClose).toHaveBeenCalled();
    })
    it("displays the icon", async () => {
        const {getByTestId} = render(<Status value={status} icon={<PlusOneOutlined/>} onClose={jest.fn()} />);
        getByTestId("PlusOneOutlinedIcon");
    })
});
