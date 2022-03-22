import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SnackbarProvider } from "notistack";

import Alert from "./Alert";
import { AlertMessage } from "../../context/taipyReducers";

const defaultMessage = "message";
const defaultAlert: AlertMessage = { atype: "success", message: defaultMessage, system: true, duration: 3000 };

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
    it("displays a success alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={defaultAlert} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantSuccess")).toBeInTheDocument()
    });
    it("displays an error alert", async () => {
        const { getByText } = render(<SnackbarProvider><Alert alert={{...defaultAlert, atype:"error"}} /></SnackbarProvider>);
        const elt = getByText(defaultMessage);
        expect(elt.closest(".SnackbarItem-variantError")).toBeInTheDocument()
    });
    it("displays a warning alert", async () => {
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
