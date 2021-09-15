import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";

import { ENDPOINT } from "../utils";

export enum Types {
    Update = 'UPDATE',
    SendUpdate = 'SEND_UPDATE_ACTION',
    Action = 'SEND_ACTION_ACTION',
    RequestTableUpdate = 'REQUEST_TABLE_UPDATE'
}

export interface TaipyState {
    socket?: Socket;
    data: any;
}

export interface TaipyAction {
    type: Types;
    name: string;
    payload: any;
}

export const taipyInitialize = (initialState: TaipyState) => ({
    ...initialState,
    socket: io(ENDPOINT)
})

export const initializeWebSocket = (socket: Socket | undefined, dispatch: Dispatch<TaipyAction>) => {
    if (socket) {
        // Websocket confirm successful initialization
        socket.on('connect', () => {
            console.log('CONNECTED');
            socket?.send({ status: 'Connected!'});
        });
        socket.on('disconnect', () => {
            console.log('DISCONNECTED');
            socket?.send({status: 'Disconnected!'});
        });
        // handle message data from backend
        socket.on('message', (message: WsMessage) => {
            if (message.type && message.type == 'U' && message.name) { // interestingly we can't use === for message.type here 8-|
                dispatch(createUpdateAction(message.name, message.payload))
            }
        });
    }

}

export const taipyReducer = (state: TaipyState, action: TaipyAction) => {
    switch (action.type) {
        case Types.Update:
            return {...state, data: { ...state.data, [action.name]: action.payload.pagekey ? {...state.data[action.name], [action.payload.pagekey]: action.payload.value} : action.payload.value}};
        case Types.SendUpdate:
            sendWsMessage(state.socket, 'U', action.name, action.payload.value);
            break;
        case Types.Action:
            sendWsMessage(state.socket, 'A', action.name, action.payload.value);
            break;
        case Types.RequestTableUpdate:
            sendWsMessage(state.socket, 'T', action.name, action.payload);
            break;
    }
    return state;
}

export const createUpdateAction = (name: string, payload: any) => ({
    type: Types.Update,
    name: name.replaceAll('.', '__'),
    payload: payload
} as TaipyAction)

export const createSendUpdateAction = (name: string, value: any) => ({
    type: Types.SendUpdate,
    name: name,
    payload: {value: value}
} as TaipyAction)

export const createSendActionNameAction = (name: string, value: any) => ({
    type: Types.Action,
    name: name,
    payload: {value: value}
} as TaipyAction)

export const createRequestTableUpdateAction = (name: string, id: string, pageKey: string, start?: number, end?: number) => ({
    type: Types.RequestTableUpdate,
    name: name,
    payload: {
        id: id,
        pagekey: pageKey,
        start: start,
        end: end
    }
} as TaipyAction)

type WsMessageType = "A" | "U" | "T";

interface WsMessage {
    type: WsMessageType;
    name: string;
    payload: any;
}

const sendWsMessage = (socket: Socket | undefined, type: WsMessageType, name: string, payload: any) => {
    const msg: WsMessage = {type: type, name: name, payload: payload};
    socket?.emit("message", msg);
};
