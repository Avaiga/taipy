import merge from "lodash/merge";
import { TaipyApp } from "./app";
import { IdMessage, storeClientId } from "../../src/context/utils";
import { WsMessage } from "../../src/context/wsUtils";
import { DataManager, getRequestedDataKey, ModuleData } from "./dataManager";

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
        this.supportedMessageTypes = ["MU", "ID", "GMC", "GDT", "AID", "GR", "AL", "ACK"];
        this.initWsMessageTypes = ["ID", "AID", "GMC"];
    }
    handleWsMessage(message: WsMessage, taipyApp: TaipyApp): boolean {
        if (message.type) {
            if (message.type === "MU" && Array.isArray(message.payload)) {
                for (const muPayload of message.payload as [MultipleUpdatePayload]) {
                    const encodedName = muPayload.name;
                    const { value } = muPayload.payload;
                    if (value && typeof (value as any).__taipy_refresh === "boolean") {
                        // refresh all requested data for this encodedName var
                        const requestDataOptions = taipyApp.variableData?._requested_data[encodedName];
                        for (const dataKey in requestDataOptions) {
                            const requestDataEntry = requestDataOptions[dataKey];
                            const { options } = requestDataEntry;
                            taipyApp.sendWsMessage("DU", encodedName, options);
                        }
                        return true;
                    }
                    const dataKey = getRequestedDataKey(muPayload.payload);
                    taipyApp.variableData?.update(encodedName, value, dataKey);
                    // call the callback if it exists for request data
                    if (dataKey && (encodedName in taipyApp._rdc && dataKey in taipyApp._rdc[encodedName])) {
                        const cb = taipyApp._rdc[encodedName]?.[dataKey];
                        cb(taipyApp, encodedName, dataKey, value);
                        delete taipyApp._rdc[encodedName][dataKey];
                    }
                    taipyApp.onChangeEvent(encodedName, value, dataKey);
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
