import { PaletteMode } from "@mui/material";
import { createTheme, Theme } from "@mui/material/styles";
import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";
import merge from "lodash/merge";

import { ENDPOINT, TIMEZONE_CLIENT } from "../utils";
import { parseData } from "../utils/dataFormat";
import { MenuProps } from "../utils/lov";

enum Types {
    SocketConnected = "SOCKET_CONNECTED",
    Update = "UPDATE",
    MultipleUpdate = "MULTIPLE_UPDATE",
    SendUpdate = "SEND_UPDATE_ACTION",
    Action = "SEND_ACTION_ACTION",
    RequestDataUpdate = "REQUEST_DATA_UPDATE",
    RequestUpdate = "REQUEST_UPDATE",
    SetLocations = "SET_LOCATIONS",
    SetTheme = "SET_THEME",
    SetTimeZone = "SET_TIMEZONE",
    SetAlert = "SET_ALERT",
    SetBlock = "SET_BLOCK",
    Navigate = "NAVIGATE",
    ClientId = "CLIENT_ID",
    MultipleMessages = "MULTIPLE_MESSAGES",
    SetMenu = "SET_MENU",
}

export interface TaipyState {
    socket?: Socket;
    isSocketConnected?: boolean;
    data: Record<string, unknown>;
    theme: Theme;
    locations: Record<string, string>;
    timeZone: string;
    dateTimeFormat?: string;
    numberFormat?: string;
    alert?: AlertMessage;
    block?: BlockMessage;
    to?: string;
    id: string;
    menu: MenuProps;
}

export interface TaipyBaseAction {
    type: Types;
}

interface NamePayload {
    name: string;
    payload: Record<string, unknown>;
}

export interface AlertMessage {
    atype: string;
    message: string;
    browser: boolean;
    duration: number;
}

interface TaipyAction extends NamePayload, TaipyBaseAction {
    propagate?: boolean;
}

interface TaipyMultipleAction extends TaipyBaseAction {
    payload: NamePayload[];
}

interface TaipyMultipleMessageAction extends TaipyBaseAction {
    actions: TaipyBaseAction[];
}

interface TaipyAlertAction extends TaipyBaseAction, AlertMessage {}

export const BLOCK_CLOSE = { action: "", message: "", close: true, noCancel: false } as BlockMessage;

export interface BlockMessage {
    action: string;
    noCancel: boolean;
    close: boolean;
    message: string;
}

interface TaipyBlockAction extends TaipyBaseAction, BlockMessage {}

interface NavigateMessage {
    to?: string;
}

interface TaipyNavigateAction extends TaipyBaseAction, NavigateMessage {}

interface IdMessage {
    id: string;
}

interface TaipyIdAction extends TaipyBaseAction, IdMessage {}

interface TaipySetMenuAction extends TaipyBaseAction {
    menu: MenuProps;
}

export interface FormatConfig {
    timeZone: string;
    dateTime: string;
    number: string;
}

const getUserTheme = (mode: PaletteMode) => {
    const userTheme = window.taipyUserThemes?.base || {};
    const modeTheme = (window.taipyUserThemes && window.taipyUserThemes[mode]) || {};
    return createTheme(
        merge(userTheme, modeTheme, {
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
        })
    );
};

const themes = {
    light: getUserTheme("light"),
    dark: getUserTheme("dark"),
};

const getLocalStorageValue = <T = string>(key: string, defaultValue: T, values?: T[]) => {
    const val = localStorage && (localStorage.getItem(key) as unknown as T);
    return !val ? defaultValue : !values ? val : values.indexOf(val) == -1 ? defaultValue : val;
};

export const INITIAL_STATE: TaipyState = {
    data: {},
    theme: themes.light,
    locations: {},
    timeZone: TIMEZONE_CLIENT,
    id: getLocalStorageValue("TaipyClientId", ""),
    menu: {},
};

export const taipyInitialize = (initialState: TaipyState): TaipyState => ({
    ...initialState,
    isSocketConnected: false,
    socket: io(ENDPOINT),
});

const storeClientId = (id: string) => localStorage && localStorage.setItem("TaipyClientId", id);

const messageToAction = (message: WsMessage) => {
    if (message.type) {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            return createMultipleUpdateAction(message.payload as NamePayload[]);
        } else if (message.type === "MS" && Array.isArray(message.payload)) {
            return createMultipleMessagesAction(message.payload as WsMessage[]);
        } else if (message.type === "AL") {
            return createAlertAction(message as unknown as AlertMessage);
        } else if (message.type === "BL") {
            return createBlockAction(message as unknown as BlockMessage);
        } else if (message.type === "NA") {
            return createNavigateAction((message as unknown as NavigateMessage).to);
        } else if (message.type === "ID") {
            return createIdAction((message as unknown as IdMessage).id);
        }
    }
    return {} as TaipyBaseAction;
};

export const initializeWebSocket = (socket: Socket | undefined, dispatch: Dispatch<TaipyBaseAction>): void => {
    if (socket) {
        // Websocket confirm successful initialization
        socket.on("connect", () => {
            const id = getLocalStorageValue("TaipyClientId", "");
            sendWsMessage(socket, "ID", "TaipyClientId", id, id);
            dispatch({ type: Types.SocketConnected });
        });
        // handle message data from backend
        socket.on("message", (message: WsMessage) => dispatch(messageToAction(message)));
    }
};

const addRows = (previousRows: Record<string, unknown>[], newRows: Record<string, unknown>[], start: number) =>
    newRows.reduce((arr, row) => {
        arr[start++] = row;
        return arr;
    }, previousRows.concat([]));

const storeBlockUi = (block?: BlockMessage) => () => {
    if (localStorage) {
        if (block) {
            document.visibilityState !== "visible" && localStorage.setItem("TaipyBlockUi", JSON.stringify(block));
        } else {
            localStorage.removeItem("TaipyBlockUi");
        }
    }
};

export const retreiveBlockUi = (): BlockMessage => {
    if (localStorage) {
        const val = localStorage.getItem("TaipyBlockUi");
        if (val) {
            try {
                return JSON.parse(val);
            } catch {
                // too bad
            }
        }
    }
    return {} as BlockMessage;
};

export const taipyReducer = (state: TaipyState, baseAction: TaipyBaseAction): TaipyState => {
    const action = baseAction as TaipyAction;
    switch (action.type) {
        case Types.SocketConnected:
            return !!state.isSocketConnected ? state : { ...state, isSocketConnected: true };
        case Types.Update:
            const newValue = parseData(action.payload.value as Record<string, unknown>);
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
        case Types.SetLocations:
            return { ...state, locations: action.payload.value as Record<string, string> };
        case Types.SetAlert:
            const alertAction = action as unknown as TaipyAlertAction;
            if (alertAction.atype) {
                return {
                    ...state,
                    alert: {
                        atype: alertAction.atype,
                        message: alertAction.message,
                        browser: alertAction.browser,
                        duration: alertAction.duration,
                    },
                };
            }
            delete state.alert;
            return { ...state };
        case Types.SetBlock:
            const blockAction = action as unknown as TaipyBlockAction;
            if (blockAction.close) {
                storeBlockUi()();
                delete state.block;
                return { ...state };
            } else {
                document.onvisibilitychange = storeBlockUi(blockAction as BlockMessage);
                return {
                    ...state,
                    block: {
                        noCancel: blockAction.noCancel,
                        action: blockAction.action,
                        close: false,
                        message: blockAction.message,
                    },
                };
            }
        case Types.Navigate:
            return { ...state, to: (action as unknown as TaipyNavigateAction).to };
        case Types.ClientId:
            const id = (action as unknown as TaipyIdAction).id;
            storeClientId(id);
            return { ...state, id: id };
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
            if (!action.payload.fromBackend) {
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
        case Types.SetMenu: {
            const mAction = baseAction as TaipySetMenuAction;
            return { ...state, menu: mAction.menu };
        }
        case Types.MultipleUpdate:
            const mAction = baseAction as TaipyMultipleAction;
            return mAction.payload.reduce((nState, pl) => taipyReducer(nState, { ...pl, type: Types.Update }), state);
        case Types.MultipleMessages:
            const msgAction = baseAction as TaipyMultipleMessageAction;
            return msgAction.actions.reduce((pState, act) => taipyReducer(pState, act), state);
        case Types.SendUpdate:
            sendWsMessage(state.socket, "U", action.name, action.payload, state.id, action.propagate);
            break;
        case Types.Action:
            sendWsMessage(state.socket, "A", action.name, action.payload, state.id);
            break;
        case Types.RequestDataUpdate:
            sendWsMessage(state.socket, "DU", action.name, action.payload, state.id);
            break;
        case Types.RequestUpdate:
            sendWsMessage(state.socket, "RU", action.name, action.payload, state.id);
            break;
    }
    return state;
};

const createMultipleUpdateAction = (payload: NamePayload[]): TaipyMultipleAction => ({
    type: Types.MultipleUpdate,
    payload: payload,
});

export const createSendUpdateAction = (
    name: string | undefined,
    value: unknown,
    propagate = true,
    type = ""
): TaipyAction => ({
    type: Types.SendUpdate,
    name: name || "",
    propagate: propagate,
    payload: { value: value, type: type },
});

export const createSendActionNameAction = (
    name: string | undefined,
    value: unknown,
    ...args: unknown[]
): TaipyAction => ({
    type: Types.Action,
    name: name || "",
    payload: { action: value, args: args },
});

export const createRequestChartUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    columns: string[],
    width: number | undefined
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
    sort?: string,
    aggregates?: string[],
    applies?: Record<string, unknown>,
    styles?: Record<string, unknown>,
    handleNan?: boolean
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
        aggregates: aggregates,
        applies: applies,
        styles: styles,
        handlenan: handleNan,
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
    sort?: string,
    aggregates?: string[],
    applies?: Record<string, unknown>,
    styles?: Record<string, unknown>,
    handleNan?: boolean
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
        aggregates: aggregates,
        applies: applies,
        styles: styles,
        handlenan: handleNan,
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
    payload: { timeZone: timeZone, fromBackend: fromBackend },
});

const getAlertType = (aType: string) => {
    aType = aType.trim() || "i";
    aType = aType.substr(0, 1).toLowerCase();
    switch (aType) {
        case "e":
            return "error";
        case "w":
            return "warning";
        case "s":
            return "success";
        default:
            return "info";
    }
};

export const createAlertAction = (alert?: AlertMessage): TaipyAlertAction => ({
    type: Types.SetAlert,
    atype: alert ? getAlertType(alert.atype) : "",
    message: alert ? alert.message : "",
    browser: alert ? alert.browser : true,
    duration: alert ? alert.duration : 3000,
});

export const createBlockAction = (block: BlockMessage): TaipyBlockAction => ({
    type: Types.SetBlock,
    noCancel: block.noCancel,
    action: block.action || "",
    close: !!block.close,
    message: block.message,
});

export const createNavigateAction = (to?: string): TaipyNavigateAction => ({
    type: Types.Navigate,
    to: to,
});

export const createIdAction = (id: string): TaipyIdAction => ({
    type: Types.ClientId,
    id: id,
});

export const createSetMenuAction = (menu: MenuProps): TaipySetMenuAction => ({
    type: Types.SetMenu,
    menu: menu,
});

export const createMultipleMessagesAction = (messages: WsMessage[]): TaipyMultipleMessageAction => ({
    type: Types.MultipleMessages,
    actions: messages.map(messageToAction),
});

type WsMessageType = "A" | "U" | "DU" | "MU" | "RU" | "AL" | "BL" | "NA" | "ID" | "MS";

interface WsMessage {
    type: WsMessageType;
    name: string;
    payload: Record<string, unknown> | unknown;
    propagate: boolean;
    client_id: string;
}

const sendWsMessage = (
    socket: Socket | undefined,
    type: WsMessageType,
    name: string,
    payload: Record<string, unknown> | unknown,
    id: string,
    propagate = true
): void => {
    const msg: WsMessage = { type: type, name: name, payload: payload, propagate: propagate, client_id: id };
    socket?.emit("message", msg);
};
