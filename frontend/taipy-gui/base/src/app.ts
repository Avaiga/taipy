import { getLocalStorageValue } from "../../src/context/utils";
import { sendWsMessage, TAIPY_CLIENT_ID } from "../../src/context/wsUtils";
import { uploadFile } from "../../src/workers/fileupload";

import { Socket, io } from "socket.io-client";
import { VariableManager } from "./variableManager";
import { initSocket } from "./utils";

export type OnInitHandler = (appManager: TaipyApp) => void;
export type OnChangeHandler = (appManager: TaipyApp, encodedName: string, value: unknown) => void;

export class TaipyApp {
    socket: Socket;
    _onInit: OnInitHandler | undefined;
    _onChange: OnChangeHandler | undefined;
    variableManager: VariableManager | undefined;
    appId: string;
    clientId: string;
    context: string;
    path: string | undefined;

    constructor(
        onInit: OnInitHandler | undefined = undefined,
        onChange: OnChangeHandler | undefined = undefined,
        path: string | undefined = undefined,
        socket: Socket | undefined = undefined
    ) {
        socket = socket || io("/", { autoConnect: false });
        this.onInit = onInit;
        this.onChange = onChange;
        this.variableManager = undefined;
        this.clientId = "";
        this.context = "";
        this.appId = "";
        this.path = path;
        this.socket = socket;
        initSocket(socket, this);
    }

    // Getter and setter
    get onInit() {
        return this._onInit;
    }
    set onInit(handler: OnInitHandler | undefined) {
        if (handler !== undefined && handler?.length !== 1) {
            throw new Error("onInit() requires one parameter");
        }
        this._onInit = handler;
    }

    get onChange() {
        return this._onChange;
    }
    set onChange(handler: OnChangeHandler | undefined) {
        if (handler !== undefined && handler?.length !== 3) {
            throw new Error("onChange() requires three parameters");
        }
        this._onChange = handler;
    }

    // Utility methods
    init() {
        this.clientId = "";
        this.context = "";
        this.appId = "";
        const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
        sendWsMessage(this.socket, "ID", TAIPY_CLIENT_ID, id, id, undefined, false);
        sendWsMessage(this.socket, "AID", "connect", "", id, undefined, false);
        if (id !== "") {
            this.clientId = id;
            this.updateContext(this.path);
        }
    }

    // Public methods
    getEncodedName(varName: string, module: string) {
        return this.variableManager?.getEncodedName(varName, module);
    }

    getName(encodedName: string) {
        return this.variableManager?.getName(encodedName);
    }

    get(encodedName: string) {
        return this.variableManager?.get(encodedName);
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

    trigger(actionName: string, triggerId: string, payload: Record<string, unknown> = {}) {
        payload["action"] = actionName;
        sendWsMessage(this.socket, "A", triggerId, payload, this.clientId, this.context);
    }

    upload(encodedName: string, files: FileList, progressCallback: (val: number) => void) {
        return uploadFile(encodedName, files, progressCallback, this.clientId);
    }
}

export const createApp = (onInit?: OnInitHandler, onChange?: OnChangeHandler, path?: string, socket?: Socket) => {
    return new TaipyApp(onInit, onChange, path, socket);
};
