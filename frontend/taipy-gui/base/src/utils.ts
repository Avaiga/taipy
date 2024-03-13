import { Socket } from "socket.io-client";
import { IdMessage, storeClientId } from "../../src/context/utils";
import { WsMessage, sendWsMessage } from "../../src/context/wsUtils";
import { TaipyApp } from "./app";
import { DataManager, ModuleData } from "./dataManager";

interface MultipleUpdatePayload {
    name: string;
    payload: { value: unknown };
}

interface AlertMessage extends WsMessage {
    atype: string;
    message: string;
}

const initWsMessageTypes = ["ID", "AID", "GMC"];

export const initSocket = (socket: Socket, appManager: TaipyApp) => {
    socket.on("connect", () => {
        if (appManager.clientId === "" || appManager.appId === "") {
            appManager.init();
        }
    });
    // Send a request to get App ID to verify that the app has not been reloaded
    socket.io.on("reconnect", () => {
        console.log("WebSocket reconnected")
        sendWsMessage(socket, "AID", "reconnect", appManager.appId, appManager.clientId, appManager.context);
    });
    // try to reconnect on connect_error
    socket.on("connect_error", (err) => {
        console.log("Error connecting WebSocket: ", err);
        setTimeout(() => {
            socket && socket.connect();
        }, 500);
    });
    // try to reconnect on server disconnection
    socket.on("disconnect", (reason, details) => {
        console.log("WebSocket disconnected due to: ", reason, details);
        if (reason === "io server disconnect") {
            socket && socket.connect();
        }
    });
    // handle message data from backend
    socket.on("message", (message: WsMessage) => {
        processWsMessage(message, appManager);
    });
    // only now does the socket tries to open/connect
    if (!socket.connected) {
        socket.connect();
    }
};

const processWsMessage = (message: WsMessage, appManager: TaipyApp) => {
    if (message.type) {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            for (const muPayload of message.payload as [MultipleUpdatePayload]) {
                const encodedName = muPayload.name;
                const { value } = muPayload.payload;
                appManager.variableData?.update(encodedName, value);
                appManager.onChange && appManager.onChange(appManager, encodedName, value);
            }
        } else if (message.type === "ID") {
            const { id } = message as unknown as IdMessage;
            storeClientId(id);
            appManager.clientId = id;
            appManager.updateContext(appManager.path);
        } else if (message.type === "GMC") {
            const mc = (message.payload as Record<string, unknown>).data as string;
            window.localStorage.setItem("ModuleContext", mc);
            appManager.context = mc;
        } else if (message.type === "GDT") {
            const payload = message.payload as Record<string, ModuleData>;
            const variableData = payload.variable;
            const functionData = payload.function;
            if (appManager.variableData && appManager.functionData) {
                appManager.variableData.init(variableData);
                appManager.functionData.init(functionData);
            } else {
                appManager.variableData = new DataManager(variableData);
                appManager.functionData = new DataManager(functionData);
                appManager.onInit && appManager.onInit(appManager);
            }
        } else if (message.type === "AID") {
            const payload = message.payload as Record<string, unknown>;
            if (payload.name === "reconnect") {
                return appManager.init();
            }
            appManager.appId = payload.id as string;
        } else if (message.type === "AL" && appManager.onNotify) {
            const payload = message as AlertMessage;
            appManager.onNotify(appManager, payload.atype, payload.message);
        }
        postWsMessageProcessing(message, appManager);
    }
};

const postWsMessageProcessing = (message: WsMessage, appManager: TaipyApp) => {
    // perform data population only when all necessary metadata is ready
    if (
        initWsMessageTypes.includes(message.type) &&
        appManager.clientId !== "" &&
        appManager.appId !== "" &&
        appManager.context !== ""
    ) {
        sendWsMessage(appManager.socket, "GDT", "get_data_tree", {}, appManager.clientId, appManager.context);
    }
};
