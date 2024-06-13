import { getLocalStorageValue } from "../../src/context/utils";
import { sendWsMessage, TAIPY_CLIENT_ID } from "../../src/context/wsUtils";
import { uploadFile } from "../../src/workers/fileupload";

import { Socket, io } from "socket.io-client";
import { DataManager, ModuleData } from "./dataManager";
import { initSocket } from "./socket";
import { TaipyWsAdapter, WsAdapter } from "./wsAdapter";

export type OnInitHandler = (taipyApp: TaipyApp) => void;
export type OnChangeHandler = (taipyApp: TaipyApp, encodedName: string, value: unknown) => void;
export type OnNotifyHandler = (taipyApp: TaipyApp, type: string, message: string) => void;
export type OnReloadHandler = (taipyApp: TaipyApp, removedChanges: ModuleData) => void;
type Route = [string, string];

export class TaipyApp {
    socket: Socket;
    _onInit: OnInitHandler | undefined;
    _onChange: OnChangeHandler | undefined;
    _onNotify: OnNotifyHandler | undefined;
    _onReload: OnReloadHandler | undefined;
    variableData: DataManager | undefined;
    functionData: DataManager | undefined;
    appId: string;
    clientId: string;
    context: string;
    path: string | undefined;
    routes: Route[] | undefined;
    wsAdapters: WsAdapter[];

    constructor(
        onInit: OnInitHandler | undefined = undefined,
        onChange: OnChangeHandler | undefined = undefined,
        path: string | undefined = undefined,
        socket: Socket | undefined = undefined,
    ) {
        socket = socket || io("/", { autoConnect: false });
        this.onInit = onInit;
        this.onChange = onChange;
        this.variableData = undefined;
        this.functionData = undefined;
        this.clientId = "";
        this.context = "";
        this.appId = "";
        this.routes = undefined;
        this.path = path;
        this.socket = socket;
        this.wsAdapters = [new TaipyWsAdapter()];
        initSocket(socket, this);
    }

    // Getter and setter
    get onInit() {
        return this._onInit;
    }

    set onInit(handler: OnInitHandler | undefined) {
        if (handler !== undefined && handler.length !== 1) {
            throw new Error("onInit() requires one parameter");
        }
        this._onInit = handler;
    }

    get onChange() {
        return this._onChange;
    }

    set onChange(handler: OnChangeHandler | undefined) {
        if (handler !== undefined && handler.length !== 3) {
            throw new Error("onChange() requires three parameters");
        }
        this._onChange = handler;
    }

    get onNotify() {
        return this._onNotify;
    }

    set onNotify(handler: OnNotifyHandler | undefined) {
        if (handler !== undefined && handler.length !== 3) {
            throw new Error("onNotify() requires three parameters");
        }
        this._onNotify = handler;
    }

    get onReload() {
        return this._onReload;
    }
    set onReload(handler: OnReloadHandler | undefined) {
        if (handler !== undefined && handler?.length !== 2) {
            throw new Error("_onReload() requires two parameters");
        }
        this._onReload = handler;
    }

    // Utility methods
    init() {
        this.clientId = "";
        this.context = "";
        this.appId = "";
        this.routes = undefined;
        const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
        sendWsMessage(this.socket, "ID", TAIPY_CLIENT_ID, id, id, undefined, false);
        sendWsMessage(this.socket, "AID", "connect", "", id, undefined, false);
        sendWsMessage(this.socket, "GR", "", "", id, undefined, false);
        if (id !== "") {
            this.clientId = id;
            this.updateContext(this.path);
        }
    }

    // Public methods
    registerWsAdapter(wsAdapter: WsAdapter) {
        this.wsAdapters.push(wsAdapter);
    }

    getEncodedName(varName: string, module: string) {
        return this.variableData?.getEncodedName(varName, module);
    }

    getName(encodedName: string) {
        return this.variableData?.getName(encodedName);
    }

    get(encodedName: string) {
        return this.variableData?.get(encodedName);
    }

    getInfo(encodedName: string) {
        return this.variableData?.getInfo(encodedName);
    }

    getDataTree() {
        return this.variableData?.getDataTree();
    }

    getAllData() {
        return this.variableData?.getAllData();
    }

    getFunctionList() {
        const functionData = this.functionData?.getDataTree()[this.context];
        return Object.keys(functionData || {});
    }

    getRoutes() {
        return this.routes;
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

    getPageMetadata() {
        return JSON.parse(localStorage.getItem("tp_cp_meta") || "{}");
    }
}

export const createApp = (onInit?: OnInitHandler, onChange?: OnChangeHandler, path?: string, socket?: Socket) => {
    return new TaipyApp(onInit, onChange, path, socket);
};
