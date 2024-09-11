import merge from "lodash/merge";
import { TaipyApp } from "./app";
import { IdMessage, storeClientId } from "../../src/context/utils";
import { WsMessage } from "../../src/context/wsUtils";
import { DataManager, ModuleData } from "./dataManager";

export abstract class WsAdapter {
    abstract supportedMessageTypes: string[];

    abstract handleWsMessage(message: WsMessage, app: TaipyApp): boolean;
}

interface MultipleUpdatePayload {
    name: string;
    payload: { value: unknown };
}

interface AlertMessage extends WsMessage {
    atype: string;
    message: string;
}

export class TaipyWsAdapter extends WsAdapter {
    supportedMessageTypes: string[];
    initWsMessageTypes: string[];
    constructor() {
        super();
        this.supportedMessageTypes = ["MU", "ID", "GMC", "GDT", "AID", "GR", "AL", "ACK", "RU"];
        this.initWsMessageTypes = ["ID", "AID", "GMC"];
    }
    handleWsMessage(message: WsMessage, taipyApp: TaipyApp): boolean {
        if (message.type) {
            if (message.type === "MU" && Array.isArray(message.payload)) {
                for (const muPayload of message.payload as [MultipleUpdatePayload]) {
                    const encodedName = muPayload.name;
                    const { value } = muPayload.payload;
                    if (value && typeof (value as any).__taipy_refresh === "boolean") {
                        // here we know that we can request an DU for this variable
                        // Question is how to get the right payload ?
                    }
                    taipyApp.variableData?.update(encodedName, value);
                    taipyApp.onChangeEvent(encodedName, value);
                }
            } else if (message.type === "ID") {
                const { id } = message as unknown as IdMessage;
                storeClientId(id);
                taipyApp.clientId = id;
                taipyApp.updateContext(taipyApp.path);
            } else if (message.type === "GMC") {
                const payload = message.payload as Record<string, unknown>;
                taipyApp.context = payload.context as string;
                if (payload?.metadata) {
                    try {
                        taipyApp.metadata = JSON.parse((payload.metadata as string) || "{}");
                    } catch (e) {
                        console.error("Error parsing metadata from Taipy Designer", e);
                    }
                }
            } else if (message.type === "GDT") {
                const payload = message.payload as Record<string, ModuleData>;
                const variableData = payload.variable;
                const functionData = payload.function;
                if (taipyApp.variableData && taipyApp.functionData) {
                    const varChanges = taipyApp.variableData.init(variableData);
                    const functionChanges = taipyApp.functionData.init(functionData);
                    const changes = merge(varChanges, functionChanges);
                    if (varChanges || functionChanges) {
                        taipyApp.onReloadEvent(changes);
                    }
                } else {
                    taipyApp.variableData = new DataManager(variableData);
                    taipyApp.functionData = new DataManager(functionData);
                    taipyApp.onInitEvent();
                }
            } else if (message.type === "AID") {
                const payload = message.payload as Record<string, unknown>;
                if (payload.name === "reconnect") {
                    taipyApp.init();
                    return true;
                }
                taipyApp.appId = payload.id as string;
            } else if (message.type === "GR") {
                const payload = message.payload as [string, string][];
                taipyApp.routes = payload;
            } else if (message.type === "AL") {
                const payload = message as AlertMessage;
                taipyApp.onNotifyEvent(payload.atype, payload.message);
            } else if (message.type === "ACK") {
                const { id } = message as unknown as Record<string, string>;
                taipyApp._ackList = taipyApp._ackList.filter((v) => v !== id);
                taipyApp.onWsStatusUpdateEvent(taipyApp._ackList);
            } else if (message.type === "RU") {
                const payload = message.payload as Record<string, unknown>;
                // process to get data
                const data = {};
                const encodedName = "";
                const dataEventKey = "";
                // add data to cache
                taipyApp.addRequestedData(encodedName, dataEventKey, data);
                // get and execute callback
                const callbackName = taipyApp.getRequestedDataName(encodedName, dataEventKey);
                const requestedDataCallback = taipyApp._rdc[callbackName];
                if (requestedDataCallback) {
                    requestedDataCallback(taipyApp, encodedName, dataEventKey, data);
                    // remove callback after usage
                    delete taipyApp._rdc[callbackName];
                }
            }
            this.postWsMessageProcessing(message, taipyApp);
            return true;
        }
        return false;
    }
    postWsMessageProcessing(message: WsMessage, taipyApp: TaipyApp) {
        // perform data population only when all necessary metadata is ready
        if (
            this.initWsMessageTypes.includes(message.type) &&
            taipyApp.clientId !== "" &&
            taipyApp.appId !== "" &&
            taipyApp.context !== "" &&
            taipyApp.routes !== undefined
        ) {
            taipyApp.sendWsMessage("GDT", "get_data_tree", {});
        }
    }
}
