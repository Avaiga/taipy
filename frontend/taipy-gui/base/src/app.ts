import { getLocalStorageValue } from "../../src/context/utils";
import { sendWsMessage, TAIPY_CLIENT_ID } from "../../src/context/wsUtils";
import { uploadFile } from "../../src/workers/fileupload";

import { Socket, io } from "socket.io-client";
import { nanoid } from "nanoid";
import { DataManager, ModuleData, RequestDataOptions } from "./dataManager";
import { initSocket } from "./socket";
import { TaipyWsAdapter, WsAdapter } from "./wsAdapter";
import { WsMessageType } from "../../src/context/wsUtils";
import { getBase } from "./utils";

export type OnInitHandler = (taipyApp: TaipyApp) => void;
export type OnChangeHandler = (taipyApp: TaipyApp, encodedName: string, value: unknown, dataEventKey?: string) => void;
export type OnNotifyHandler = (taipyApp: TaipyApp, type: string, message: string) => void;
export type OnReloadHandler = (taipyApp: TaipyApp, removedChanges: ModuleData) => void;
export type OnWsMessage = (taipyApp: TaipyApp, event: string, payload: unknown) => void;
export type OnWsStatusUpdate = (taipyApp: TaipyApp, messageQueue: string[]) => void;
export type OnEvent =
    | OnInitHandler
    | OnChangeHandler
    | OnNotifyHandler
    | OnReloadHandler
    | OnWsMessage
    | OnWsStatusUpdate;
type Route = [string, string];
type RequestDataCallback = (taipyApp: TaipyApp, encodedName: string, dataEventKey: string, value: unknown) => void;

export class TaipyApp {
    socket: Socket;
    _onInit: OnInitHandler | undefined;
    _onChange: OnChangeHandler | undefined;
    _onNotify: OnNotifyHandler | undefined;
    _onReload: OnReloadHandler | undefined;
    _onWsMessage: OnWsMessage | undefined;
    _onWsStatusUpdate: OnWsStatusUpdate | undefined;
    _ackList: string[];
    _rdc: Record<string, Record<string, RequestDataCallback>>;
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
        socket: Socket | undefined = undefined,
    ) {
        socket = socket || io("/", { autoConnect: false, path: `${this.getBaseUrl()}socket.io` });
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
        this._rdc = {};
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

    onInitEvent() {
        this.onInit && this.onInit(this);
    }

    get onChange() {
        return this._onChange;
    }

    set onChange(handler: OnChangeHandler | undefined) {
        if (handler !== undefined && handler.length !== 3 && handler.length !== 4) {
            throw new Error("onChange() requires three or four parameters");
        }
        this._onChange = handler;
    }

    onChangeEvent(encodedName: string, value: unknown, dataEventKey?: string) {
        this.onChange && this.onChange(this, encodedName, value, dataEventKey);
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

    onNotifyEvent(type: string, message: string) {
        this.onNotify && this.onNotify(this, type, message);
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

    onReloadEvent(removedChanges: ModuleData) {
        this.onReload && this.onReload(this, removedChanges);
    }

    get onWsMessage() {
        return this._onWsMessage;
    }
    set onWsMessage(handler: OnWsMessage | undefined) {
        if (handler !== undefined && handler?.length !== 3) {
            throw new Error("onWsMessage() requires three parameters");
        }
        this._onWsMessage = handler;
    }

    onWsMessageEvent(event: string, payload: unknown) {
        this.onWsMessage && this.onWsMessage(this, event, payload);
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

    onWsStatusUpdateEvent(messageQueue: string[]) {
        this.onWsStatusUpdate && this.onWsStatusUpdate(this, messageQueue);
    }

    // Utility methods
    init() {
        this.clientId = "";
        this.context = "";
        this.appId = "";
        this.routes = undefined;
        const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
        this.sendWsMessage("ID", TAIPY_CLIENT_ID, id);
        if (id !== "") {
            this.clientId = id;
            this.initApp()
            this.updateContext(this.path);
        }
    }

    initApp() {
        this.sendWsMessage("AID", "connect", "");
        this.sendWsMessage("GR", "", "");
    }

    sendWsMessage(type: WsMessageType, id: string, payload: unknown, context: string | undefined = undefined) {
        if (context === undefined) {
            context = this.context;
        }
        const ackId = sendWsMessage(this.socket, type, id, payload, this.clientId, context);
        if (ackId) {
            this._ackList.push(ackId);
            this.onWsStatusUpdateEvent(this._ackList);
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

    get(encodedName: string, dataEventKey?: string) {
        return this.variableData?.get(encodedName, dataEventKey);
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

    deleteRequestedData(encodedName: string, dataEventKey: string) {
        this.variableData?.deleteRequestedData(encodedName, dataEventKey);
    }

    // This update will only send the request to Taipy Gui backend
    // the actual update will be handled when the backend responds
    update(encodedName: string, value: unknown) {
        this.sendWsMessage("U", encodedName, { value: value });
    }

    // Request Data from taipy backend
    // This will trigger the backend to send the data to the frontend
    requestData(encodedName: string, cb: RequestDataCallback, options?: RequestDataOptions) {
        const varInfo = this.getInfo(encodedName);
        if (!varInfo?.data_update) {
            throw new Error(`Cannot request data for ${encodedName}. Not supported for type of ${varInfo?.type}`);
        }
        // Populate pagekey if there is no pagekey
        if (!options) {
            options = { pagekey: nanoid(10) };
        }
        options.pagekey = options?.pagekey || nanoid(10);
        const dataKey = options.pagekey;
        // preserve options for this data key so it can be called during refresh
        this.variableData?.addRequestDataOptions(encodedName, dataKey, options);
        // preserve callback so it can be called later
        this._rdc[encodedName] = { ...this._rdc[encodedName], [dataKey]: cb };
        // call the ws to request data
        this.sendWsMessage("DU", encodedName, options);
    }

    getContext() {
        return this.context;
    }

    updateContext(path: string | undefined = "") {
        if (!path || path === "") {
            path = window.location.pathname.replace(this.getBaseUrl(), "") || "/";
        }
        this.sendWsMessage("GMC", "get_module_context", { path: path || "/" });
    }

    trigger(actionName: string, triggerId: string, payload: Record<string, unknown> = {}) {
        payload["action"] = actionName;
        this.sendWsMessage("A", triggerId, payload);
    }

    upload(encodedName: string, files: FileList, progressCallback: (val: number) => void) {
        return uploadFile(encodedName, undefined, undefined, undefined, files, progressCallback, this.clientId);
    }

    getPageMetadata() {
        return this.metadata;
    }

    getWsStatus() {
        return this._ackList;
    }

    getBaseUrl() {
        return getBase();
    }
}

export const createApp = (onInit?: OnInitHandler, onChange?: OnChangeHandler, path?: string, socket?: Socket) => {
    return new TaipyApp(onInit, onChange, path, socket);
};
