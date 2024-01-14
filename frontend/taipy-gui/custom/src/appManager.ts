import { sendWsMessage } from "../../src/context/wsUtils";

import { Socket, io } from "socket.io-client";
import { VariableManager } from "./variableManager";
import { initSocket } from "./utils";

export type OnInitHandler = (appManager: AppManager) => void;
export type OnUpdateHandler = (appManager: AppManager, encodedName: string, value: unknown) => void;

export class AppManager {
    socket: Socket;
    onInit: OnInitHandler | undefined;
    onUpdate: OnUpdateHandler | undefined;
    variableManager: VariableManager | undefined;
    clientId: string;
    context: string;
    path: string | undefined;

    constructor(
        onInit: OnInitHandler | undefined = undefined,
        onUpdate: OnUpdateHandler | undefined = undefined,
        path: string | undefined = undefined,
        socket: Socket | undefined = undefined
    ) {
        socket = socket || io("/", { autoConnect: false });
        this.onInit = onInit;
        this.onUpdate = onUpdate;
        this.variableManager = undefined;
        this.clientId = "";
        this.context = "";
        this.path = path;
        this.socket = socket;
        initSocket(socket, this);
    }

    getEncodedName(varName: string, module: string) {
        return this.variableManager?.getEncodedName(varName, module);
    }

    getName(encodedName: string) {
        return this.variableManager?.getName(encodedName);
    }

    get(varName: string) {
        return this.variableManager?.get(varName);
    }

    getInfo(encodedName: string) {
        return this.variableManager?.getInfo(encodedName);
    }

    getDataTree() {
        return this.variableManager?.getDataTree();
    }

    getAllData() {
        return this.variableManager?.getAllData();
    }

    // This update will only send the request to Taipy Gui backend
    // the actual update will be handled when the backend responds
    update(encodedName: string, value: unknown) {
        sendWsMessage(this.socket, "U", encodedName, { value: value }, this.clientId, this.context);
    }

    getContext() {
        return this.context;
    }

    updateContext(path: string | undefined = "") {
        if (!path || path === "") {
            path = window.location.pathname.slice(1);
        }
        sendWsMessage(this.socket, "GMC", "get_module_context", { path: path }, this.clientId);
    }
}

export const createAppManager = (
    onInit?: OnInitHandler,
    onUpdate?: OnUpdateHandler,
    path?: string,
    socket?: Socket
) => {
    return new AppManager(onInit, onUpdate, path, socket);
};
