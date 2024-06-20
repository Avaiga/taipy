import { Socket } from "socket.io-client";

export type ModuleData = Record<string, VarName>;
export type VarName = Record<string, VarData>;
export interface VarData {
    type: string;
    value: unknown;
    encoded_name: string;
}
declare class DataManager {
    _data: Record<string, unknown>;
    _init_data: ModuleData;
    constructor(variableModuleData: ModuleData);
    init(variableModuleData: ModuleData): ModuleData;
    getEncodedName(varName: string, module: string): string | undefined;
    getName(encodedName: string): [string, string] | undefined;
    get(encodedName: string): unknown;
    getInfo(encodedName: string): VarData | undefined;
    getDataTree(): ModuleData;
    getAllData(): Record<string, unknown>;
    update(encodedName: string, value: unknown): void;
}
export type OnInitHandler = (taipyApp: TaipyApp) => void;
export type OnChangeHandler = (taipyApp: TaipyApp, encodedName: string, value: unknown) => void;
export type OnNotifyHandler = (taipyApp: TaipyApp, type: string, message: string) => void;
export type OnReloadHandler = (taipyApp: TaipyApp, removedChanges: ModuleData) => void;
export type Route = [string, string];
export declare class TaipyApp {
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
        onInit?: OnInitHandler | undefined,
        onChange?: OnChangeHandler | undefined,
        path?: string | undefined,
        socket?: Socket | undefined
    );
    get onInit(): OnInitHandler | undefined;
    set onInit(handler: OnInitHandler | undefined);
    get onChange(): OnChangeHandler | undefined;
    set onChange(handler: OnChangeHandler | undefined);
    get onNotify(): OnNotifyHandler | undefined;
    set onNotify(handler: OnNotifyHandler | undefined);
    get onReload(): OnReloadHandler | undefined;
    set onReload(handler: OnReloadHandler | undefined);
    init(): void;
    registerWsAdapter(wsAdapter: WsAdapter): void;
    getEncodedName(varName: string, module: string): string | undefined;
    getName(encodedName: string): [string, string] | undefined;
    get(encodedName: string): unknown;
    getInfo(encodedName: string): VarData | undefined;
    getDataTree(): ModuleData | undefined;
    getAllData(): Record<string, unknown> | undefined;
    getFunctionList(): string[];
    getRoutes(): Route[] | undefined;
    update(encodedName: string, value: unknown): void;
    getContext(): string;
    updateContext(path?: string | undefined): void;
    trigger(actionName: string, triggerId: string, payload?: Record<string, unknown>): void;
    upload(encodedName: string, files: FileList, progressCallback: (val: number) => void): Promise<string>;
    getPageMetadata(): any;
}
export type WsMessageType =
    | "A"
    | "U"
    | "DU"
    | "MU"
    | "RU"
    | "AL"
    | "BL"
    | "NA"
    | "ID"
    | "MS"
    | "DF"
    | "PR"
    | "ACK"
    | "GMC"
    | "GDT"
    | "AID"
    | "GR";
export interface WsMessage {
    type: WsMessageType | str;
    name: string;
    payload: Record<string, unknown> | unknown;
    propagate: boolean;
    client_id: string;
    module_context: string;
    ack_id?: string;
}
export declare const sendWsMessage: (
    socket: Socket | undefined,
    type: WsMessageType | str,
    name: string,
    payload: Record<string, unknown> | unknown,
    id: string,
    moduleContext?: string,
    propagate?: boolean,
    serverAck?: (val: unknown) => void
) => string;
export declare abstract class WsAdapter {
    abstract supportedMessageTypes: string[];
    abstract handleWsMessage(message: WsMessage, app: TaipyApp): boolean;
}
