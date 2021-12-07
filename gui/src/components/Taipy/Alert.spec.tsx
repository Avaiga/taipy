import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { SnackbarProvider } from "notistack";

import Alert from "./Alert";
import { AlertMessage, INITIAL_STATE, TaipyState } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

const defaultMessage = "message";
const defaultAlert: AlertMessage = { atype: "success", message: defaultMessage, browser: true };

class myNotification {
    static requestPermission = jest.fn();
    static permission = "granted";
}

describe("Alert Component", () => {
    beforeAll(() => {
        globalThis.Notification = myNotification as unknown as jest.Mocked<typeof Notification>;
    });
    it("renders", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={defaultAlert} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.tagName).toBe("DIV");
    });
    it("removes the current alert", async () => {
        const dispatch = jest.fn();
        const state: TaipyState = INITIAL_STATE;
        const { getByText, getByTestId } = render(<TaipyContext.Provider value={{ state, dispatch }}><SnackbarProvider><Alert alert={defaultAlert} /></SnackbarProvider></TaipyContext.Provider>);
        const elt = getByText(defaultMessage);
        const butt = getByTestId("CloseIcon");
        userEvent.click(butt);
        expect(dispatch).toHaveBeenCalledWith({"atype": "", "message": "", "type": "SET_ALERT", browser: true});
    });
    it("displays an success alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={defaultAlert} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantSuccess")).toBeInTheDocument()
    });
    it("displays an error alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={{...defaultAlert, atype:"error"}} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantError")).toBeInTheDocument()
    });
    it("displays an warning alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={{...defaultAlert, atype:"warning"}} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantWarning")).toBeInTheDocument()
    });
    it("displays an info alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={{...defaultAlert, atype:"info"}} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantInfo")).toBeInTheDocument()
    });
});
