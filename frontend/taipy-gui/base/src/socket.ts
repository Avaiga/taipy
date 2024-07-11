import { Socket } from "socket.io-client";
import { WsMessage } from "../../src/context/wsUtils";
import { TaipyApp } from "./app";

export const initSocket = (socket: Socket, taipyApp: TaipyApp) => {
    socket.on("connect", () => {
        taipyApp.useEvent(taipyApp.onWsMessage, "connect", null);
        if (taipyApp.clientId === "" || taipyApp.appId === "") {
            taipyApp.init();
        }
    });
    // Send a request to get App ID to verify that the app has not been reloaded
    socket.io.on("reconnect", () => {
        taipyApp.useEvent(taipyApp.onWsMessage, "reconnect", null);
        console.log("WebSocket reconnected");
        taipyApp.sendWsMessage("AID", "reconnect", taipyApp.appId);
    });
    // try to reconnect on connect_error
    socket.on("connect_error", (err) => {
        taipyApp.useEvent(taipyApp.onWsMessage, "connect_error", { err });
        console.log("Error connecting WebSocket: ", err);
        setTimeout(() => {
            socket && socket.connect();
        }, 500);
    });
    // try to reconnect on server disconnection
    socket.on("disconnect", (reason, details) => {
        taipyApp.useEvent(taipyApp.onWsMessage, "disconnect", { reason, details });
        console.log("WebSocket disconnected due to: ", reason, details);
        if (reason === "io server disconnect") {
            socket && socket.connect();
        }
    });
    // handle message data from backend
    socket.on("message", (message: WsMessage) => {
        taipyApp.useEvent(taipyApp.onWsMessage, "message", message);
        // handle messages with registered websocket adapters
        for (const adapter of taipyApp.wsAdapters) {
            if (adapter.supportedMessageTypes.includes(message.type)) {
                const messageResolved = adapter.handleWsMessage(message, taipyApp);
                if (messageResolved) {
                    return;
                }
            }
        }
    });
    // only now does the socket tries to open/connect
    if (!socket.connected) {
        socket.connect();
    }
};
