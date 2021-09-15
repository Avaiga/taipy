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
    value: string;
}

export interface TaipyTableAction extends TaipyAction {
    id: string;
    start?: number;
    end?: number;
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
                dispatch(createUpdateAction(message.name, message.payload.value))
            }
        });
    }

}

export const taipyReducer = (state: TaipyState, action: TaipyAction) => {
    switch (action.type) {
        case Types.Update:
            return {...state, data: { ...state.data, [action.name]: action.value}};
        case Types.SendUpdate:
            sendWsMessage(state.socket, 'U', action.name, {value: action.value});
            break;
        case Types.Action:
            sendWsMessage(state.socket, 'A', action.name, {action: action.value});
            break;
        case Types.RequestTableUpdate:
            const tAction = action as TaipyTableAction;
            sendWsMessage(state.socket, 'T', action.name, {id: tAction.id, start: tAction.start, end: tAction.end});
            break;
    }
    return state;
}

export const createUpdateAction = (name: string, value: any) => ({
    type: Types.Update,
    name: name.replaceAll('.', '__'),
    value: value
} as TaipyAction)

export const createSendUpdateAction = (name: string, value: any) => ({
    type: Types.SendUpdate,
    name: name,
    value: value
} as TaipyAction)

export const createSendActionNameAction = (name: string, value: any) => ({
    type: Types.Action,
    name: name,
    value: value
} as TaipyAction)

export const createRequestTableUpdateAction = (name: string, id: string, start?: number, end?: number) => ({
    type: Types.RequestTableUpdate,
    name: name,
    id: id,
    start: start,
    end: end
} as TaipyTableAction)

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
