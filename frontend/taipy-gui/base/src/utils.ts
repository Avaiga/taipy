import merge from "lodash/merge";
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

export const initSocket = (socket: Socket, taipyApp: TaipyApp) => {
    socket.on("connect", () => {
        if (taipyApp.clientId === "" || taipyApp.appId === "") {
            taipyApp.init();
        }
    });
    // Send a request to get App ID to verify that the app has not been reloaded
    socket.io.on("reconnect", () => {
        console.log("WebSocket reconnected")
        sendWsMessage(socket, "AID", "reconnect", taipyApp.appId, taipyApp.clientId, taipyApp.context);
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
        processWsMessage(message, taipyApp);
    });
    // only now does the socket tries to open/connect
    if (!socket.connected) {
        socket.connect();
    }
};

const processWsMessage = (message: WsMessage, taipyApp: TaipyApp) => {
    if (message.type) {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            for (const muPayload of message.payload as [MultipleUpdatePayload]) {
                const encodedName = muPayload.name;
                const { value } = muPayload.payload;
                taipyApp.variableData?.update(encodedName, value);
                taipyApp.onChange && taipyApp.onChange(taipyApp, encodedName, value);
            }
        } else if (message.type === "ID") {
            const { id } = message as unknown as IdMessage;
            storeClientId(id);
            taipyApp.clientId = id;
            taipyApp.updateContext(taipyApp.path);
        } else if (message.type === "GMC") {
            const mc = (message.payload as Record<string, unknown>).data as string;
            window.localStorage.setItem("ModuleContext", mc);
            taipyApp.context = mc;
        } else if (message.type === "GDT") {
            const payload = message.payload as Record<string, ModuleData>;
            const variableData = payload.variable;
            const functionData = payload.function;
            if (taipyApp.variableData && taipyApp.functionData) {
                const varChanges = taipyApp.variableData.init(variableData);
                const functionChanges = taipyApp.functionData.init(functionData);
                const changes = merge(varChanges, functionChanges);
                if (varChanges || functionChanges) {
                    taipyApp.onReload && taipyApp.onReload(taipyApp, changes);
                }
            } else {
                taipyApp.variableData = new DataManager(variableData);
                taipyApp.functionData = new DataManager(functionData);
                taipyApp.onInit && taipyApp.onInit(taipyApp);
            }
        } else if (message.type === "AID") {
            const payload = message.payload as Record<string, unknown>;
            if (payload.name === "reconnect") {
                return taipyApp.init();
            }
            taipyApp.appId = payload.id as string;
        } else if (message.type === "GR") {
            const payload = message.payload as [string, string][];
            taipyApp.routes = payload;
        } else if (message.type === "AL" && taipyApp.onNotify) {
            const payload = message as AlertMessage;
            taipyApp.onNotify(taipyApp, payload.atype, payload.message);
        }
        postWsMessageProcessing(message, taipyApp);
    }
};

const postWsMessageProcessing = (message: WsMessage, taipyApp: TaipyApp) => {
    // perform data population only when all necessary metadata is ready
    if (
        initWsMessageTypes.includes(message.type) &&
        taipyApp.clientId !== "" &&
        taipyApp.appId !== "" &&
        taipyApp.context !== "" &&
        taipyApp.routes !== undefined
    ) {
        sendWsMessage(taipyApp.socket, "GDT", "get_data_tree", {}, taipyApp.clientId, taipyApp.context);
    }
};
