import { sendWsMessage } from "../../src/context/wsUtils";
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
            throw new Error("onInit function requires 1 parameter");
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

    // Public methods
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

    trigger(actionName: string, triggerId: string, payload: Record<string, unknown> = {}) {
        payload["action"] = actionName;
        sendWsMessage(this.socket, "A", triggerId, payload, this.clientId, this.context);
    }

    uploadFile(encodedName: string, files: FileList, progressCallback: (val: number) => void) {
        return uploadFile(encodedName, files, progressCallback, this.clientId);
    }
}

export const createApp = (onInit?: OnInitHandler, onChange?: OnChangeHandler, path?: string, socket?: Socket) => {
    return new TaipyApp(onInit, onChange, path, socket);
};
