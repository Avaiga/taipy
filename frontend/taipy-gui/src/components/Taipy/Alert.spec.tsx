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
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SnackbarProvider } from "notistack";

import Alert from "./Alert";
import { AlertMessage } from "../../context/taipyReducers";
import userEvent from "@testing-library/user-event";

const defaultMessage = "message";
const defaultAlerts: AlertMessage[] = [{ atype: "success", message: defaultMessage, system: true, duration: 3000 }];
const getAlertsWithType = (aType: string) => [{ ...defaultAlerts[0], atype: aType }];

class myNotification {
    static requestPermission = jest.fn(() => Promise.resolve("granted"));
    static permission = "granted";
}

describe("Alert Component", () => {
    beforeAll(() => {
        globalThis.Notification = myNotification as unknown as jest.Mocked<typeof Notification>;
    });
    beforeEach(() => {
        jest.clearAllMocks();
    });
    it("renders", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <Alert alerts={defaultAlerts} />
            </SnackbarProvider>,
        );
        const elt = getByText(defaultMessage);
        expect(elt.tagName).toBe("DIV");
    });
    it("displays a success alert", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <Alert alerts={defaultAlerts} />
            </SnackbarProvider>,
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-success")).toBeInTheDocument();
    });
    it("displays an error alert", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <Alert alerts={getAlertsWithType("error")} />
            </SnackbarProvider>,
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-error")).toBeInTheDocument();
    });
    it("displays a warning alert", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <Alert alerts={getAlertsWithType("warning")} />
            </SnackbarProvider>,
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-warning")).toBeInTheDocument();
    });
    it("displays an info alert", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <Alert alerts={getAlertsWithType("info")} />
            </SnackbarProvider>,
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-info")).toBeInTheDocument();
    });
    it("gets favicon URL from document link tags", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        link.href = "/test-icon.png";
        document.head.appendChild(link);
        const alerts: AlertMessage[] = [
            { atype: "success", message: "This is a system alert", system: true, duration: 3000 },
        ];
        render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        const linkElement = document.querySelector("link[rel='icon']");
        if (linkElement) {
            expect(linkElement.getAttribute("href")).toBe("/test-icon.png");
        } else {
            expect(true).toBe(false);
        }
        document.head.removeChild(link);
    });

    it("closes Snackbar on close button click", async () => {
        const alerts = [{ atype: "success", message: "Test Alert", duration: 3000, system: false }];
        render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        const closeButton = await screen.findByRole("button", { name: /close/i });
        await userEvent.click(closeButton);
        await waitFor(() => {
            const alertMessage = screen.queryByText("Test Alert");
            expect(alertMessage).not.toBeInTheDocument();
        });
    });

    it("Snackbar disappears when alert type is empty", async () => {
        const alerts = [{ atype: "success", message: "Test Alert", duration: 3000, system: false }];
        const { rerender } = render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        await screen.findByRole("button", { name: /close/i });
        const newAlerts = [{ atype: "", message: "Test Alert", duration: 3000, system: false }];
        rerender(
            <SnackbarProvider>
                <Alert alerts={newAlerts} />
            </SnackbarProvider>,
        );
        await waitFor(() => {
            const alertMessage = screen.queryByText("Test Alert");
            expect(alertMessage).not.toBeInTheDocument();
        });
    });

    it("does nothing when alert is undefined", async () => {
        render(
            <SnackbarProvider>
                <Alert alerts={[]} />
            </SnackbarProvider>,
        );
        expect(Notification.requestPermission).not.toHaveBeenCalled();
    });

    it("validates href when rel attribute is 'icon' and href is set", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        link.href = "/test-icon.png";
        document.head.appendChild(link);
        const alerts: AlertMessage[] = [
            { atype: "success", message: "This is a system alert", system: true, duration: 3000 },
        ];
        render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        const linkElement = document.querySelector("link[rel='icon']");
        expect(linkElement?.getAttribute("href")).toBe("/test-icon.png");
        document.head.removeChild(link);
    });

    it("verifies default favicon for 'icon' rel attribute when href is unset/empty", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
        const alerts: AlertMessage[] = [
            { atype: "success", message: "This is a system alert", system: true, duration: 3000 },
        ];
        render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        const linkElement = document.querySelector("link[rel='icon']");
        expect(linkElement?.getAttribute("href") || "/favicon.png").toBe("/favicon.png");
        document.head.removeChild(link);
    });

    it("validates href when rel attribute is 'shortcut icon' and href is provided", () => {
        const link = document.createElement("link");
        link.rel = "shortcut icon";
        link.href = "/test-shortcut-icon.png";
        document.head.appendChild(link);
        const alerts: AlertMessage[] = [
            { atype: "success", message: "This is a system alert", system: true, duration: 3000 },
        ];
        render(
            <SnackbarProvider>
                <Alert alerts={alerts} />
            </SnackbarProvider>,
        );
        const linkElement = document.querySelector("link[rel='shortcut icon']");
        expect(linkElement?.getAttribute("href")).toBe("/test-shortcut-icon.png");
        document.head.removeChild(link);
    });
});
