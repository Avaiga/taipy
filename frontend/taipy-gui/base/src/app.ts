import { getLocalStorageValue } from "../../src/context/utils";
import { sendWsMessage, TAIPY_CLIENT_ID } from "../../src/context/wsUtils";
import { uploadFile } from "../../src/workers/fileupload";

import { Socket, io } from "socket.io-client";
import { DataManager, ModuleData } from "./dataManager";
import { initSocket } from "./socket";
import { TaipyWsAdapter, WsAdapter } from "./wsAdapter";
import { WsMessageType } from "../../src/context/wsUtils";

export type OnInitHandler = (taipyApp: TaipyApp) => void;
export type OnChangeHandler = (taipyApp: TaipyApp, encodedName: string, value: unknown) => void;
export type OnNotifyHandler = (taipyApp: TaipyApp, type: string, message: string) => void;
export type OnReloadHandler = (taipyApp: TaipyApp, removedChanges: ModuleData) => void;
export type OnWsStatusUpdate = (taipyApp: TaipyApp, messageQueue: string[]) => void;
type Route = [string, string];

export class TaipyApp {
    socket: Socket;
    _onInit: OnInitHandler | undefined;
    _onChange: OnChangeHandler | undefined;
    _onNotify: OnNotifyHandler | undefined;
    _onReload: OnReloadHandler | undefined;
    _onWsStatusUpdate: OnWsStatusUpdate | undefined;
    _ackList: string[];
    variableData: DataManager | undefined;
    functionData: DataManager | undefined;
    appId: string;
    clientId: string;
    context: string;
    metadata: Record<string, unknown>;
    path: string | undefined;
    routes: Route[] | undefined;
    wsAdapters: WsAdapter[];

    constructor(
        onInit: OnInitHandler | undefined = undefined,
        onChange: OnChangeHandler | undefined = undefined,
        path: string | undefined = undefined,
        socket: Socket | undefined = undefined
    ) {
        socket = socket || io("/", { autoConnect: false });
        this.onInit = onInit;
        this.onChange = onChange;
        this.variableData = undefined;
        this.functionData = undefined;
        this.clientId = "";
        this.context = "";
        this.metadata = {};
        this.appId = "";
        this.routes = undefined;
        this.path = path;
        this.socket = socket;
        this.wsAdapters = [new TaipyWsAdapter()];
        this._ackList = [];
        // Init socket io connection
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
            throw new Error("onReload() requires two parameters");
        }
        this._onReload = handler;
    }

    get onWsStatusUpdate() {
        return this._onWsStatusUpdate;
    }
    set onWsStatusUpdate(handler: OnWsStatusUpdate | undefined) {
        if (handler !== undefined && handler?.length !== 2) {
            throw new Error("onWsStatusUpdate() requires two parameters");
        }
        this._onWsStatusUpdate = handler;
    }

    // Utility methods
    init() {
        this.clientId = "";
        this.context = "";
        this.appId = "";
        this.routes = undefined;
        const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
        this.sendWsMessage("ID", TAIPY_CLIENT_ID, id);
        this.sendWsMessage("AID", "connect", "");
        this.sendWsMessage("GR", "", "");
        if (id !== "") {
            this.clientId = id;
            this.updateContext(this.path);
        }
    }

    sendWsMessage(type: WsMessageType, id: string, payload: unknown, context: string | undefined = undefined) {
        if (context === undefined) {
            context = this.context;
        }
        const ackId = sendWsMessage(this.socket, type, id, payload, this.clientId, context);
        if (ackId) {
            this._ackList.push(ackId);
            this.onWsStatusUpdate && this.onWsStatusUpdate(this, this._ackList);
        }
    }

    // Public methods
    registerWsAdapter(wsAdapter: WsAdapter) {
        this.wsAdapters.unshift(wsAdapter);
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
        this.sendWsMessage("U", encodedName, { value: value });
    }

    getContext() {
        return this.context;
    }

    updateContext(path: string | undefined = "") {
        if (!path || path === "") {
            path = window.location.pathname.slice(1);
        }
        this.sendWsMessage("GMC", "get_module_context", { path: path || "/" });
    }

    trigger(actionName: string, triggerId: string, payload: Record<string, unknown> = {}) {
        payload["action"] = actionName;
        this.sendWsMessage("A", triggerId, payload);
    }

    upload(encodedName: string, files: FileList, progressCallback: (val: number) => void) {
        return uploadFile(encodedName, files, progressCallback, this.clientId);
    }

    getPageMetadata() {
        return this.metadata;
    }

    getWsStatus() {
        return this._ackList;
    }
}

export const createApp = (onInit?: OnInitHandler, onChange?: OnChangeHandler, path?: string, socket?: Socket) => {
    return new TaipyApp(onInit, onChange, path, socket);
};
