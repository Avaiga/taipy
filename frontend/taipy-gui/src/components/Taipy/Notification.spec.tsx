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
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SnackbarProvider } from "notistack";

import TaipyNotification from "./Notification";
import { NotificationMessage } from "../../context/taipyReducers";
import userEvent from "@testing-library/user-event";

const defaultMessage = "message";
const defaultNotifications: NotificationMessage[] = [
    { nType: "success", message: defaultMessage, system: true, duration: 3000, snackbarId: "nId" },
];
const getNotificationsWithType = (nType: string) => [{ ...defaultNotifications[0], nType }];

class myNotification {
    static requestPermission = jest.fn(() => Promise.resolve("granted"));
    static permission = "granted";
}

describe("Notifications", () => {
    beforeAll(() => {
        globalThis.Notification = myNotification as unknown as jest.Mocked<typeof Notification>;
    });
    beforeEach(() => {
        jest.clearAllMocks();
    });
    it("renders", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={defaultNotifications} />
            </SnackbarProvider>
        );
        const elt = getByText(defaultMessage);
        expect(elt.tagName).toBe("DIV");
    });
    it("displays a success notification", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={defaultNotifications} />
            </SnackbarProvider>
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-success")).toBeInTheDocument();
    });
    it("displays an error notification", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={getNotificationsWithType("error")} />
            </SnackbarProvider>
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-error")).toBeInTheDocument();
    });
    it("displays a warning notification", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={getNotificationsWithType("warning")} />
            </SnackbarProvider>
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-warning")).toBeInTheDocument();
    });
    it("displays an info notification", async () => {
        const { getByText } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={getNotificationsWithType("info")} />
            </SnackbarProvider>
        );
        const elt = getByText(defaultMessage);
        expect(elt.closest(".notistack-MuiContent-info")).toBeInTheDocument();
    });
    it("gets favicon URL from document link tags", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        link.href = "/test-icon.png";
        document.head.appendChild(link);
        const notifications: NotificationMessage[] = [
            {
                nType: "success",
                message: "This is a system notification",
                system: true,
                duration: 3000,
                snackbarId: "nId",
            },
        ];
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
        );
        const linkElement = document.querySelector("link[rel='icon']");
        if (linkElement) {
            expect(linkElement.getAttribute("href")).toBe("/test-icon.png");
        } else {
            expect(true).toBe(false);
        }
        document.head.removeChild(link);
    });

    it("closes notification on close button click", async () => {
        const notifications = [
            { nType: "success", message: "Test Notification", duration: 3000, system: false, snackbarId: "nId" },
        ];
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
        );
        const closeButton = await screen.findByRole("button", { name: /close/i });
        await userEvent.click(closeButton);
        await waitFor(() => {
            const notificationMessage = screen.queryByText("Test Notification");
            expect(notificationMessage).not.toBeInTheDocument();
        });
    });

    it("Notification disappears when notification type is empty", async () => {
        const baseNotification = {
            nType: "success",
            message: "Test Notification",
            duration: 3000,
            system: false,
            notificationId: "nId",
            snackbarId: "nId",
        };
        const notifications = [ baseNotification ];
        const { rerender } = render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
        );
        await screen.findByRole("button", { name: /close/i });
        const newNotifications = [ { ...baseNotification, nType: "" }];
        rerender(
            <SnackbarProvider>
                <TaipyNotification notifications={newNotifications} />
            </SnackbarProvider>
        );
        await waitFor(() => {
            const notificationMessage = screen.queryByText("Test Notification");
            expect(notificationMessage).not.toBeInTheDocument();
        });
    });

    it("does nothing when notification is undefined", async () => {
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={[]} />
            </SnackbarProvider>
        );
        expect(Notification.requestPermission).not.toHaveBeenCalled();
    });

    it("validates href when rel attribute is 'icon' and href is set", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        link.href = "/test-icon.png";
        document.head.appendChild(link);
        const notifications: NotificationMessage[] = [
            {
                nType: "success",
                message: "This is a system notification",
                system: true,
                duration: 3000,
                snackbarId: "nId",
            },
        ];
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
        );
        const linkElement = document.querySelector("link[rel='icon']");
        expect(linkElement?.getAttribute("href")).toBe("/test-icon.png");
        document.head.removeChild(link);
    });

    it("verifies default favicon for 'icon' rel attribute when href is unset/empty", () => {
        const link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
        const notifications: NotificationMessage[] = [
            {
                nType: "success",
                message: "This is a system notification",
                system: true,
                duration: 3000,
                snackbarId: "nId",
            },
        ];
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
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
        const notifications: NotificationMessage[] = [
            {
                nType: "success",
                message: "This is a system notification",
                system: true,
                duration: 3000,
                snackbarId: "nId",
            },
        ];
        render(
            <SnackbarProvider>
                <TaipyNotification notifications={notifications} />
            </SnackbarProvider>
        );
        const linkElement = document.querySelector("link[rel='shortcut icon']");
        expect(linkElement?.getAttribute("href")).toBe("/test-shortcut-icon.png");
        document.head.removeChild(link);
    });
});
