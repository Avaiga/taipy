/*
 * Copyright 2021-2025 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import { Socket } from "socket.io-client";
import { nanoid } from "nanoid";

export const TAIPY_CLIENT_ID = "TaipyClientId";
export const TAIPY_GUI_ADDR = "TaipyGuiAddr";

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
    | "GA"
    | "FV"
    | "BC"
    | "LS"
    | "PT";

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
    serverAck?: (val: unknown) => void,
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

// Remove all keys with undefined values from the payload to avoid errors on the backend
// Starting with ES2019, we could use a more elegant way with:
//   Object.fromEntries(Object.entries(payload).filter(([, value]) => value !== undefined));
export const lightenPayload = (payload: Record<string, unknown>) => {
    return payload
        ? Object.keys(payload).reduce(
              (pv, key) => {
                  if (payload[key] !== undefined) {
                      pv[key] = payload[key];
                  }
                  return pv;
              },
              {} as typeof payload,
          )
        : {};
};
