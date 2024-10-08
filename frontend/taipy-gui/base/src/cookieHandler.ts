import { Socket } from "socket.io-client";
import { TaipyApp } from "./app";
import { initSocket } from "./socket";
import axios from "axios";
import { getLocalStorageValue } from "../../src/context/utils";

export const TAIPY_RESOURCE_HANDLER = "tprh";

export class CookieHandler {
    resourceHandlerId: string;
    constructor() {
        this.resourceHandlerId = getLocalStorageValue(TAIPY_RESOURCE_HANDLER, "");
    }
    async init(socket: Socket, taipyApp: TaipyApp) {
        const hasValidCookies = await this.verifyCookieStatus();
        if (!hasValidCookies) {
            await this.deleteCookie();
            localStorage.removeItem(TAIPY_RESOURCE_HANDLER);
            window.location.reload();
            return;
        }
        this.addBeforeUnloadListener();
        initSocket(socket, taipyApp);
    }

    async verifyCookieStatus(): Promise<boolean> {
        // check to see if local storage has the resource handler id (potentially having a cookie)
        // If not, then some part of the code must have removed the cookie
        // or wants to remove the cookie by removing the local storage
        if (!this.resourceHandlerId) {
            return new Promise((resolve) => resolve(false));
        }
        try {
            // call to get cookie status
            const { data } = await axios.get("taipy-rh");
            // validate cookie status
            if (data?.rh_id !== this.resourceHandlerId) {
                return new Promise((resolve) => resolve(false));
            }
        } catch (error) {
            console.error("Error while validating cookie:", error);
            return new Promise((resolve) => resolve(false));
        }
        return new Promise((resolve) => resolve(true));
    }

    addBeforeUnloadListener() {
        window.addEventListener("beforeunload", () => {
            localStorage.removeItem(TAIPY_RESOURCE_HANDLER);
            this.deleteCookie();
        });
    }

    async deleteCookie() {
        await axios.delete("taipy-rh");
    }
}
