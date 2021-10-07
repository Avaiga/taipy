import { createTheme, Theme } from "@mui/material/styles";
import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";

import { ENDPOINT } from "../utils";

enum Types {
    Update = "UPDATE",
    MultipleUpdate = "MULTIPLE_UPDATE",
    SendUpdate = "SEND_UPDATE_ACTION",
    Action = "SEND_ACTION_ACTION",
    RequestTableUpdate = "REQUEST_TABLE_UPDATE",
    SetLocations = "SET_LOCATIONS",
}

export interface TaipyState {
    socket?: Socket;
    data: Record<string, unknown>;
    theme: Theme;
    locations: Record<string, string>;
}

export interface TaipyBaseAction {
    type: Types;
}

interface NamePayload {
    name: string;
    payload: Record<string, unknown>;
}

interface TaipyAction extends NamePayload, TaipyBaseAction {
    propagate?: boolean;
}

interface TaipyMultipleAction extends TaipyBaseAction {
    payload: NamePayload[];
}

export const INITIAL_STATE: TaipyState = {
    data: {},
    theme: createTheme({
        palette: {
            mode: "light",
        },
    }),
    locations: {},
};

export const taipyInitialize = (initialState: TaipyState): TaipyState => ({
    ...initialState,
    socket: io(ENDPOINT),
});

export const initializeWebSocket = (socket: Socket | undefined, dispatch: Dispatch<TaipyBaseAction>): void => {
    if (socket) {
        // Websocket confirm successful initialization
        socket.on("connect", () => {
            socket?.send({ status: "Connected!" });
        });
        socket.on("disconnect", () => {
            socket?.send({ status: "Disconnected!" });
        });
        // handle message data from backend
        socket.on("message", (message: WsMessage) => {
            if (message.type) {
                if (message.type === "U" && message.name) {
                    // interestingly we can't use === for message.type here 8-|
                    dispatch(createUpdateAction(message.name, message.payload as Record<string, unknown>));
                } else if (message.type === "MU" && Array.isArray(message.payload)) {
                    dispatch(createMultipleUpdateAction(message.payload as NamePayload[]));
                }
            }
        });
    }
};

const addRows = (previousRows: Record<string, unknown>[], newRows: Record<string, unknown>[], start: number) =>
    newRows.reduce((arr, row) => {
        arr[start++] = row;
        return arr;
    }, previousRows.concat([]));

export const taipyReducer = (state: TaipyState, baseAction: TaipyBaseAction): TaipyState => {
    const action = baseAction as TaipyAction;
    switch (action.type) {
        case Types.Update:
            const newValue = action.payload.value as Record<string, unknown>;
            const oldValue = (state.data[action.name] as Record<string, unknown>) || {};
            if (typeof action.payload.infinite === "boolean" && action.payload.infinite) {
                const start = newValue.start;
                if (typeof start === "number") {
                    const rows = ((oldValue[action.payload.pagekey as string] &&
                        (oldValue[action.payload.pagekey as string] as Record<string, unknown>).data) ||
                        []) as Record<string, unknown>[];
                    newValue.data = addRows(rows, newValue.data as Record<string, unknown>[], start);
                }
            }
            return {
                ...state,
                data: {
                    ...state.data,
                    [action.name]: action.payload.pagekey
                        ? { ...oldValue, [action.payload.pagekey as string]: newValue }
                        : newValue,
                },
            };
        case Types.MultipleUpdate:
            const mAction = baseAction as TaipyMultipleAction;
            return mAction.payload.reduce((nState, pl) => taipyReducer(nState, { ...pl, type: Types.Update }), state);
        case Types.SendUpdate:
            sendWsMessage(state.socket, "U", action.name, action.payload.value, action.propagate);
            break;
        case Types.Action:
            sendWsMessage(state.socket, "A", action.name, action.payload.value);
            break;
        case Types.RequestTableUpdate:
            sendWsMessage(state.socket, "T", action.name, action.payload);
            break;
        case Types.SetLocations:
            return { ...state, locations: action.payload.value as Record<string, string> };
    }
    return state;
};

const createUpdateAction = (name: string, payload: Record<string, unknown>): TaipyAction => ({
    type: Types.Update,
    name: name,
    payload: payload,
});

const createMultipleUpdateAction = (payload: NamePayload[]): TaipyMultipleAction => ({
    type: Types.MultipleUpdate,
    payload: payload,
});

export const createSendUpdateAction = (name: string, value: unknown, propagate = true): TaipyAction => ({
    type: Types.SendUpdate,
    name: name,
    propagate: propagate,
    payload: { value: value },
});

export const createSendActionNameAction = (name: string, value: unknown): TaipyAction => ({
    type: Types.Action,
    name: name,
    payload: { value: value },
});

export const createRequestTableUpdateAction = (
    name: string,
    id: string,
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string
): TaipyAction => ({
    type: Types.RequestTableUpdate,
    name: name,
    payload: {
        id: id,
        pagekey: pageKey,
        start: start,
        end: end,
        orderby: orderBy,
        sort: sort,
    },
});

export const createRequestInfiniteTableUpdateAction = (
    name: string,
    id: string,
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string
): TaipyAction => ({
    type: Types.RequestTableUpdate,
    name: name,
    payload: {
        id: id,
        pagekey: pageKey,
        infinite: true,
        start: start,
        end: end,
        orderby: orderBy,
        sort: sort,
    },
});

export const createSetLocationsAction = (locations: Record<string, string>): TaipyAction => ({
    type: Types.SetLocations,
    name: "locations",
    payload: { value: locations },
});

type WsMessageType = "A" | "U" | "T" | "MU";

interface WsMessage {
    type: WsMessageType;
    name: string;
    payload: Record<string, unknown> | unknown;
    propagate: boolean;
}

const sendWsMessage = (
    socket: Socket | undefined,
    type: WsMessageType,
    name: string,
    payload: Record<string, unknown> | unknown,
    propagate = true
): void => {
    const msg: WsMessage = { type: type, name: name, payload: payload, propagate: propagate };
    socket?.emit("message", msg);
};
