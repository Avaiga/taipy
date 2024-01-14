import { Socket } from "socket.io-client";
import { IdMessage, getLocalStorageValue, storeClientId } from "../../src/context/utils";
import { TAIPY_CLIENT_ID, WsMessage, sendWsMessage } from "../../src/context/wsUtils";
import { TaipyApp } from "./app";
import { VariableManager, VariableModuleData } from "./variableManager";

interface MultipleUpdatePayload {
    name: string;
    payload: { value: unknown };
}

export const initSocket = (socket: Socket, appManager: TaipyApp) => {
    socket.on("connect", () => {
        const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
        sendWsMessage(socket, "ID", TAIPY_CLIENT_ID, id, id, undefined, false);
        if (id !== "") {
            appManager.clientId = id;
            appManager.updateContext(appManager.path);
        }
    });
    // try to reconnect on connect_error
    socket.on("connect_error", () => {
        setTimeout(() => {
            socket && socket.connect();
        }, 500);
    });
    // try to reconnect on server disconnection
    socket.on("disconnect", (reason) => {
        if (reason === "io server disconnect") {
            socket && socket.connect();
        }
    });
    // handle message data from backend
    socket.on("message", (message: WsMessage) => {
        processIncomingMessage(message, appManager);
    });
    // only now does the socket tries to open/connect
    if (!socket.connected) {
        socket.connect();
    }
};

export const processIncomingMessage = (message: WsMessage, appManager: TaipyApp) => {
    if (message.type) {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            for (const muPayload of message.payload as [MultipleUpdatePayload]) {
                const encodedName = muPayload.name;
                const value = muPayload.payload.value;
                appManager.variableManager?.update(encodedName, value);
                appManager.onUpdate && appManager.onUpdate(appManager, encodedName, value);
            }
        } else if (message.type === "ID") {
            const id = (message as unknown as IdMessage).id;
            storeClientId(id);
            appManager.clientId = id;
            appManager.updateContext(appManager.path);
        } else if (message.type === "GMC") {
            const mc = (message.payload as Record<string, unknown>).data as string;
            window.localStorage.setItem("ModuleContext", mc);
            appManager.context = mc;
            sendWsMessage(appManager.socket, "GVS", "get_variables", {}, appManager.clientId, appManager.context);
        } else if (message.type === "GVS") {
            const variableData = (message.payload as Record<string, unknown>).data as VariableModuleData;
            if (appManager.variableManager) {
                appManager.variableManager.resetInitData(variableData);
            } else {
                appManager.variableManager = new VariableManager(variableData);
                appManager.onInit && appManager.onInit(appManager);
            }
        }
    }
};
