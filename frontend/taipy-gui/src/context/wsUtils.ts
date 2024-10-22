import { Socket } from "socket.io-client";
import { nanoid } from 'nanoid'

export const TAIPY_CLIENT_ID = "TaipyClientId";

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
    | "GR"
    | "FV"
    | "BC";

export interface WsMessage {
    type: WsMessageType;
    name: string;
    payload: Record<string, unknown> | unknown;
    propagate: boolean;
    client_id: string;
    module_context: string;
    ack_id?: string;
}

export const sendWsMessage = (
    socket: Socket | undefined,
    type: WsMessageType,
    name: string,
    payload: Record<string, unknown> | unknown,
    id: string,
    moduleContext = "",
    propagate = true,
    serverAck?: (val: unknown) => void
): string => {
    const ackId = nanoid();
    const msg: WsMessage = {
        type: type,
        name: name,
        payload: payload,
        propagate: propagate,
        client_id: id,
        ack_id: ackId,
        module_context: moduleContext,
    };
    socket?.emit("message", lightenPayload(msg as unknown as Record<string, unknown>), serverAck);
    return ackId;
};

export const lightenPayload = (payload: Record<string, unknown>) => {
    return Object.keys(payload || {}).reduce((pv, key) => {
        if (payload[key] !== undefined) {
            pv[key] = payload[key];
        }
        return pv;
    }, {} as typeof payload);
};
