import { Socket } from "socket.io-client";
import { v4 as uuidv4 } from "uuid";

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
    | "GR";

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
    const ackId = uuidv4();
    const msg: WsMessage = {
        type: type,
        name: name,
        payload: payload,
        propagate: propagate,
        client_id: id,
        ack_id: ackId,
        module_context: moduleContext,
    };
    socket?.emit("message", msg, serverAck);
    return ackId;
};
