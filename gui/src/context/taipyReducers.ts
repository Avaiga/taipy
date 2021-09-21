import { createTheme, Theme } from "@mui/material/styles";
import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";

import { ENDPOINT } from "../utils";

export enum Types {
    Update = 'UPDATE',
    SendUpdate = 'SEND_UPDATE_ACTION',
    Action = 'SEND_ACTION_ACTION',
    RequestTableUpdate = 'REQUEST_TABLE_UPDATE',
    SetRoutes = 'SET_ROUTES'
}

export interface TaipyState {
    socket?: Socket;
    data: Record<string, unknown>;
    theme: Theme;
    routes: string[];
}

export interface TaipyAction {
    type: Types;
    name: string;
    payload: Record<string, unknown>;
}

export const INITIAL_STATE: TaipyState = { data: {}, theme: createTheme({
    components: {
      MuiTimeline: {
        styleOverrides: {
          root: {
            backgroundColor: 'red',
          },
        }
      },
    },
  }),
  routes: []
};

export const taipyInitialize = (initialState: TaipyState): TaipyState => ({
    ...initialState,
    socket: io(ENDPOINT)
})

export const initializeWebSocket = (socket: Socket | undefined, dispatch: Dispatch<TaipyAction>): void => {
    if (socket) {
        // Websocket confirm successful initialization
        socket.on('connect', () => {
            socket?.send({ status: 'Connected!'});
        });
        socket.on('disconnect', () => {
            socket?.send({status: 'Disconnected!'});
        });
        // handle message data from backend
        socket.on('message', (message: WsMessage) => {
            if (message.type && message.type == 'U' && message.name) { // interestingly we can't use === for message.type here 8-|
                dispatch(createUpdateAction(message.name, message.payload as Record<string, unknown>))
            }
        });
    }
}

export const taipyReducer = (state: TaipyState, action: TaipyAction): TaipyState => {
    switch (action.type) {
        case Types.Update:
            return {...state, data: { ...state.data, [action.name]: action.payload.pagekey ? {...state.data[action.name] as Record<string, unknown>, [action.payload.pagekey as string]: action.payload.value} : action.payload.value}};
        case Types.SendUpdate:
            sendWsMessage(state.socket, 'U', action.name, action.payload.value);
            break;
        case Types.Action:
            sendWsMessage(state.socket, 'A', action.name, action.payload.value);
            break;
        case Types.RequestTableUpdate:
            sendWsMessage(state.socket, 'T', action.name, action.payload);
            break;
        case Types.SetRoutes:
            state.routes = action.payload.value as string[];
            break;
    }
    return state;
}

export const createUpdateAction = (name: string, payload: Record<string, unknown>): TaipyAction => ({
    type: Types.Update,
    name: name,
    payload: payload
})

export const createSendUpdateAction = (name: string, value: unknown): TaipyAction => ({
    type: Types.SendUpdate,
    name: name,
    payload: {value: value}
})

export const createSendActionNameAction = (name: string, value: unknown): TaipyAction => ({
    type: Types.Action,
    name: name,
    payload: {value: value}
})

export const createRequestTableUpdateAction = (name: string, id: string, pageKey: string, start?: number, end?: number): TaipyAction => ({
    type: Types.RequestTableUpdate,
    name: name,
    payload: {
        id: id,
        pagekey: pageKey,
        start: start,
        end: end
    }
})

export const createSetRoutesAction = (routes: string[]): TaipyAction => ({
    type: Types.SetRoutes,
    name: 'routes',
    payload: {value: routes}
})

type WsMessageType = "A" | "U" | "T";

interface WsMessage {
    type: WsMessageType;
    name: string;
    payload: Record<string, unknown> | unknown;
}

const sendWsMessage = (socket: Socket | undefined, type: WsMessageType, name: string, payload: Record<string, unknown> | unknown): void => {
    const msg: WsMessage = {type: type, name: name, payload: payload};
    socket?.emit("message", msg);
};
