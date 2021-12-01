import { PaletteMode } from "@mui/material";
import { createTheme, Theme } from "@mui/material/styles";
import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";
import { merge } from "lodash";
import { Table as ArrowTable } from "apache-arrow";

import { ENDPOINT, TIMEZONE_CLIENT } from "../utils";

enum Types {
    Update = "UPDATE",
    MultipleUpdate = "MULTIPLE_UPDATE",
    SendUpdate = "SEND_UPDATE_ACTION",
    Action = "SEND_ACTION_ACTION",
    RequestDataUpdate = "REQUEST_DATA_UPDATE",
    RequestUpdate = "REQUEST_UPDATE",
    SetLocations = "SET_LOCATIONS",
    SetTheme = "SET_THEME",
    SetTimeZone = "SET_TIMEZONE",
}

enum DataFormat {
    JSON = "JSON",
    APACHE_ARROW = "Arrow"
}

export interface TaipyState {
    socket?: Socket;
    data: Record<string, unknown>;
    theme: Theme;
    locations: Record<string, string>;
    timeZone: string;
    dateTimeFormat?: string;
    numberFormat?: string;
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

export interface FormatConfig {
    timeZone: string;
    dateTime: string;
    number: string;
}

const getUserTheme = (mode: PaletteMode) => {
    const userTheme = window.taipyUserThemes?.base || {};
    const modeTheme = (window.taipyUserThemes && window.taipyUserThemes[mode]) || {};
    return createTheme(merge(userTheme, modeTheme, {
        palette: {
            mode: mode,
        },
        components: {
            MuiUseMediaQuery: {
                defaultProps: {
                    noSsr: true,
                },
            },
        },
    }));
};

const themes = {
    light: getUserTheme("light"),
    dark: getUserTheme("dark"),
};

export const INITIAL_STATE: TaipyState = {
    data: {},
    theme: themes.light,
    locations: {},
    timeZone: TIMEZONE_CLIENT,
};

export const taipyInitialize = (initialState: TaipyState): TaipyState => ({
    ...initialState,
    socket: io(ENDPOINT),
});

const getLocalStorageValue = <T = string>(key: string, defaultValue: T, values?: T[]) => {
    const val = localStorage && (localStorage.getItem(key) as unknown as T);
    return !val ? defaultValue : !values ? val : values.indexOf(val) == -1 ? defaultValue : val;
};

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
            if (newValue?.format && newValue.format === DataFormat.APACHE_ARROW) {
                const arrowData = ArrowTable.from(new Uint8Array(newValue.data as ArrayBuffer));
                const tableHeading = arrowData.schema.fields.map((f) => f.name);
                const convertedData = [];
                for (let i = 0; i < arrowData.count(); i++) {
                    const dataRow: Record<string, any> = {};
                    for (let j = 0; j < tableHeading.length; j++) {
                        dataRow[tableHeading[j]] = arrowData.getColumnAt(j)?.get(i).valueOf();
                    }
                    convertedData.push(dataRow);
                }
                newValue.data = convertedData;
            }
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
        case Types.SetLocations:
            return { ...state, locations: action.payload.value as Record<string, string> };
        case Types.SetTheme: {
            let mode = action.payload.value as PaletteMode;
            if (action.payload.fromBackend) {
                mode = getLocalStorageValue("theme", mode, ["light", "dark"]);
            }
            localStorage && localStorage.setItem("theme", mode);
            if (mode !== state.theme.palette.mode) {
                return {
                    ...state,
                    theme: themes[mode],
                };
            }
            return state;
        }
        case Types.SetTimeZone: {
            let timeZone = (action.payload.timeZone as string) || "client";
            if (action.payload.fromBackend) {
                timeZone = getLocalStorageValue("timeZone", timeZone);
            }
            if (!timeZone || timeZone === "client") {
                timeZone = TIMEZONE_CLIENT;
            }
            localStorage && localStorage.setItem("timeZone", timeZone);
            if (timeZone !== state.timeZone) {
                return {
                    ...state,
                    timeZone: timeZone,
                };
            }
            return state;
        }
        case Types.MultipleUpdate:
            const mAction = baseAction as TaipyMultipleAction;
            return mAction.payload.reduce((nState, pl) => taipyReducer(nState, { ...pl, type: Types.Update }), state);
        case Types.SendUpdate:
            sendWsMessage(state.socket, "U", action.name, action.payload.value, action.propagate);
            break;
        case Types.Action:
            sendWsMessage(state.socket, "A", action.name, action.payload.value);
            break;
        case Types.RequestDataUpdate:
            sendWsMessage(state.socket, "DU", action.name, action.payload);
            break;
        case Types.RequestUpdate:
            sendWsMessage(state.socket, "RU", action.name, action.payload);
            break;
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

export const createSendUpdateAction = (name: string | undefined, value: unknown, propagate = true): TaipyAction => ({
    type: Types.SendUpdate,
    name: name || "",
    propagate: propagate,
    payload: { value: value },
});

export const createSendActionNameAction = (name: string | undefined, value: unknown): TaipyAction => ({
    type: Types.Action,
    name: name || "",
    payload: { value: value },
});

export const createRequestChartUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    columns: string[],
    width: number | undefined,
): TaipyAction => ({
    type: Types.RequestDataUpdate,
    name: name || "",
    payload: {
        id: id,
        columns: columns,
        alldata: true,
        width: width,
    },
});

export const createRequestTableUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    columns: string[],
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string
): TaipyAction => ({
    type: Types.RequestDataUpdate,
    name: name || "",
    payload: {
        id: id,
        columns: columns,
        pagekey: pageKey,
        start: start,
        end: end,
        orderby: orderBy,
        sort: sort,
    },
});

export const createRequestInfiniteTableUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    columns: string[],
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string
): TaipyAction => ({
    type: Types.RequestDataUpdate,
    name: name || "",
    payload: {
        id: id,
        pagekey: pageKey,
        infinite: true,
        start: start,
        end: end,
        orderby: orderBy,
        sort: sort,
        columns: columns,
    },
});

export const createRequestUpdateAction = (id: string | undefined, names: string[]): TaipyAction => ({
    type: Types.RequestUpdate,
    name: "",
    payload: {
        id: id,
        names: names,
    },
});

export const createSetLocationsAction = (locations: Record<string, string>): TaipyAction => ({
    type: Types.SetLocations,
    name: "locations",
    payload: { value: locations },
});

export const createThemeAction = (dark: boolean, fromBackend = false): TaipyAction => ({
    type: Types.SetTheme,
    name: "theme",
    payload: { value: dark ? "dark" : "light", fromBackend: fromBackend },
});

export const createTimeZoneAction = (timeZone: string, fromBackend = false): TaipyAction => ({
    type: Types.SetTimeZone,
    name: "timeZone",
    payload: { value: timeZone, fromBackend: fromBackend },
});

type WsMessageType = "A" | "U" | "DU" | "MU" | "RU";

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
