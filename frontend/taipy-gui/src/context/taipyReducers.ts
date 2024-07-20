/*
 * Copyright 2021-2024 Avaiga Private Limited
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

import { PaletteMode } from "@mui/material";
import { createTheme, Theme } from "@mui/material/styles";
import merge from "lodash/merge";
import { Dispatch } from "react";
import { io, Socket } from "socket.io-client";

import { FilterDesc } from "../components/Taipy/TableFilter";
import { stylekitModeThemes, stylekitTheme } from "../themes/stylekit";
import { getBaseURL, TIMEZONE_CLIENT } from "../utils";
import { parseData } from "../utils/dataFormat";
import { MenuProps } from "../utils/lov";
import { changeFavicon, getLocalStorageValue, IdMessage, storeClientId } from "./utils";
import { ligthenPayload, sendWsMessage, TAIPY_CLIENT_ID, WsMessage } from "./wsUtils";

export enum Types {
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
    DeleteAlert = "DELETE_ALERT",
    SetBlock = "SET_BLOCK",
    Navigate = "NAVIGATE",
    ClientId = "CLIENT_ID",
    MultipleMessages = "MULTIPLE_MESSAGES",
    SetMenu = "SET_MENU",
    DownloadFile = "DOWNLOAD_FILE",
    Partial = "PARTIAL",
    Acknowledgement = "ACKNOWLEDGEMENT",
}

/**
 * The state of the underlying Taipy application.
 */
export interface TaipyState {
    socket?: Socket;
    isSocketConnected?: boolean;
    data: Record<string, unknown>;
    theme: Theme;
    locations: Record<string, string>;
    timeZone?: string;
    dateFormat?: string;
    dateTimeFormat?: string;
    numberFormat?: string;
    alerts: AlertMessage[];
    block?: BlockMessage;
    navigateTo?: string;
    navigateParams?: Record<string, string>;
    navigateTab?: string;
    navigateForce?: boolean;
    id: string;
    menu: MenuProps;
    download?: FileDownloadProps;
    ackList: string[];
}

/**
 * Application actions as used by the application reducer.
 */
export interface TaipyBaseAction {
    type: Types;
}

export interface NamePayload {
    name: string;
    payload: Record<string, unknown>;
}

export interface AlertMessage {
    atype: string;
    message: string;
    system: boolean;
    duration: number;
}

interface TaipyAction extends NamePayload, TaipyBaseAction {
    propagate?: boolean;
    context?: string;
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

export interface NavigateMessage {
    to?: string;
    params?: Record<string, string>;
    tab?: string;
    force?: boolean;
}

interface TaipyNavigateAction extends TaipyBaseAction, NavigateMessage {}

export interface FileDownloadProps {
    content?: string;
    name?: string;
    onAction?: string;
}

interface TaipyIdAction extends TaipyBaseAction, IdMessage {}

interface TaipyAckAction extends TaipyBaseAction, IdMessage {}

interface TaipyDownloadAction extends TaipyBaseAction, FileDownloadProps {}

interface TaipySetMenuAction extends TaipyBaseAction {
    menu: MenuProps;
}

interface TaipyPartialAction extends TaipyBaseAction {
    name: string;
    create: boolean;
}

export interface FormatConfig {
    timeZone: string;
    forceTZ: boolean;
    date: string;
    dateTime: string;
    number: string;
}

const getUserTheme = (mode: PaletteMode) => {
    const tkTheme = (window.taipyConfig?.stylekit && stylekitTheme) || {};
    const tkModeTheme = (window.taipyConfig?.stylekit && stylekitModeThemes[mode]) || {};
    const userTheme = window.taipyConfig?.themes?.base || {};
    const modeTheme = (window.taipyConfig?.themes && window.taipyConfig.themes[mode]) || {};
    return createTheme(
        merge(tkTheme, tkModeTheme, userTheme, modeTheme, {
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
        }),
    );
};

const themes = {
    light: getUserTheme("light"),
    dark: getUserTheme("dark"),
};

export const INITIAL_STATE: TaipyState = {
    data: {},
    theme: window.taipyConfig?.darkMode ? themes.dark : themes.light,
    locations: {},
    timeZone: window.taipyConfig?.timeZone
        ? window.taipyConfig.timeZone === "client"
            ? TIMEZONE_CLIENT
            : window.taipyConfig.timeZone
        : undefined,
    id: getLocalStorageValue(TAIPY_CLIENT_ID, ""),
    menu: {},
    ackList: [],
    alerts: [],
};

export const taipyInitialize = (initialState: TaipyState): TaipyState => ({
    ...initialState,
    isSocketConnected: false,
    socket: io("/", { autoConnect: false, path: `${getBaseURL()}socket.io` }),
});

export const messageToAction = (message: WsMessage) => {
    if (message.type) {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            return createMultipleUpdateAction(message.payload as NamePayload[]);
        } else if (message.type === "U") {
            return createUpdateAction(message as unknown as NamePayload);
        } else if (message.type === "AL") {
            return createAlertAction(message as unknown as AlertMessage);
        } else if (message.type === "BL") {
            return createBlockAction(message as unknown as BlockMessage);
        } else if (message.type === "NA") {
            return createNavigateAction(
                (message as unknown as NavigateMessage).to,
                (message as unknown as NavigateMessage).params,
                (message as unknown as NavigateMessage).tab,
                (message as unknown as NavigateMessage).force,
            );
        } else if (message.type === "ID") {
            return createIdAction((message as unknown as IdMessage).id);
        } else if (message.type === "DF") {
            return createDownloadAction(message as unknown as FileDownloadProps);
        } else if (message.type === "PR") {
            return createPartialAction((message as unknown as Record<string, string>).name, true);
        } else if (message.type === "ACK") {
            return createAckAction((message as unknown as IdMessage).id);
        } else if (message.type === "FV") {
            changeFavicon((message.payload as Record<string, string>)?.value);
        }
    }
    return {} as TaipyBaseAction;
};

export const getWsMessageListener = (dispatch: Dispatch<TaipyBaseAction>) => {
    const dispatchWsMessage = (message: WsMessage) => {
        if (message.type === "MU" && Array.isArray(message.payload)) {
            const payloads = message.payload as NamePayload[];
            Promise.all(payloads.map((pl) => parseData(pl.payload.value as Record<string, unknown>)))
                .then((vals) => {
                    vals.forEach((val, idx) => (payloads[idx].payload.value = val));
                    dispatch(messageToAction(message));
                })
                .catch(console.warn);
            return;
        } else if (message.type === "MS" && Array.isArray(message.payload)) {
            (message.payload as WsMessage[]).forEach((msg) => dispatchWsMessage(msg));
            return;
        }
        dispatch(messageToAction(message));
    };
    return dispatchWsMessage;
};

export const initializeWebSocket = (socket: Socket | undefined, dispatch: Dispatch<TaipyBaseAction>): void => {
    if (socket) {
        // Websocket confirm successful initialization
        socket.on("connect", () => {
            const id = getLocalStorageValue(TAIPY_CLIENT_ID, "");
            sendWsMessage(socket, "ID", TAIPY_CLIENT_ID, id, id, undefined, false, () => {
                dispatch({ type: Types.SocketConnected });
            });
        });
        // try to reconnect on connect_error
        socket.on("connect_error", () => {
            setTimeout(() => {
                socket.connect();
            }, 500);
        });
        // try to reconnect on server disconnection
        socket.on("disconnect", (reason) => {
            if (reason === "io server disconnect") {
                socket.connect();
            }
        });
        // handle message data from backend
        socket.on("message", getWsMessageListener(dispatch));
        // only now does the socket tries to open/connect
        socket.connect();
        changeFavicon();
    }
};

export const addRows = (previousRows: Record<string, unknown>[], newRows: Record<string, unknown>[], start: number) =>
    newRows.reduce((arr, row) => {
        arr[start++] = row;
        return arr;
    }, previousRows.concat([]));

export const storeBlockUi = (block?: BlockMessage) => () => {
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
    let ackId = "";
    switch (action.type) {
        case Types.SocketConnected:
            return !!state.isSocketConnected ? state : { ...state, isSocketConnected: true };
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
        case Types.SetLocations:
            return { ...state, locations: action.payload.value as Record<string, string> };
        case Types.SetAlert:
            const alertAction = action as unknown as TaipyAlertAction;
            return {
                ...state,
                alerts: [
                    ...state.alerts,
                    {
                        atype: alertAction.atype,
                        message: alertAction.message,
                        system: alertAction.system,
                        duration: alertAction.duration,
                    },
                ],
            };
        case Types.DeleteAlert:
            if (state.alerts.length) {
                return { ...state, alerts: state.alerts.filter((_, i) => i) };
            }
            return state;
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
            return {
                ...state,
                navigateTo: (action as unknown as TaipyNavigateAction).to,
                navigateParams: (action as unknown as TaipyNavigateAction).params,
                navigateTab: (action as unknown as TaipyNavigateAction).tab,
                navigateForce: (action as unknown as TaipyNavigateAction).force,
            };
        case Types.ClientId:
            const id = (action as unknown as TaipyIdAction).id;
            storeClientId(id);
            return { ...state, id: id };
        case Types.Acknowledgement:
            const ackList = state.ackList.filter((v) => v !== (action as unknown as TaipyAckAction).id);
            return ackList.length < state.ackList.length ? { ...state, ackList } : state;
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
        case Types.DownloadFile: {
            const dAction = baseAction as TaipyDownloadAction;
            if (dAction.content === undefined) {
                delete state.download;
                return { ...state };
            }
            return { ...state, download: { content: dAction.content, name: dAction.name, onAction: dAction.onAction } };
        }
        case Types.Partial: {
            const pAction = baseAction as TaipyPartialAction;
            const data = { ...state.data };
            if (pAction.create) {
                data[pAction.name] = true;
            } else {
                data[pAction.name] !== undefined && delete data[pAction.name];
            }
            return { ...state, data: data };
        }
        case Types.MultipleUpdate:
            const mAction = baseAction as TaipyMultipleAction;
            return mAction.payload.reduce((nState, pl) => taipyReducer(nState, { ...pl, type: Types.Update }), state);
        case Types.MultipleMessages:
            const msgAction = baseAction as TaipyMultipleMessageAction;
            return msgAction.actions.reduce((pState, act) => taipyReducer(pState, act), state);
        case Types.SendUpdate:
            ackId = sendWsMessage(
                state.socket,
                "U",
                action.name,
                action.payload,
                state.id,
                action.context,
                action.propagate,
            );
            break;
        case Types.Action:
            ackId = sendWsMessage(state.socket, "A", action.name, action.payload, state.id, action.context);
            break;
        case Types.RequestDataUpdate:
            ackId = sendWsMessage(state.socket, "DU", action.name, action.payload, state.id, action.context);
            break;
        case Types.RequestUpdate:
            ackId = sendWsMessage(state.socket, "RU", action.name, action.payload, state.id, action.context);
            break;
    }
    if (ackId) return { ...state, ackList: [...state.ackList, ackId] };
    return state;
};

export const createUpdateAction = (payload: NamePayload): TaipyAction => ({
    ...payload,
    type: Types.Update,
});

export const createMultipleUpdateAction = (payload: NamePayload[]): TaipyMultipleAction => ({
    type: Types.MultipleUpdate,
    payload: payload,
});

/**
 * Create a *send update* `Action` that will be used to update `Context`.
 *
 * This action will update the variable *name* (if *propagate* is true) and trigger the
 * invocation of the `on_change` Python function on the backend.
 * @param name - The name of the variable holding the requested data
 *    as received as a property.
 * @param value - The new value for the variable named *name*.
 * @param context - The execution context.
 * @param onChange - The name of the `on_change` Python function to
 *   invoke on the backend (default is "on_change").
 * @param propagate - A flag indicating that the variable should be
 *   automatically updated on the backend.
 * @param relName - The name of the related variable (for
 *   example the lov when a lov value is updated).
 * @returns The action fed to the reducer.
 */
export const createSendUpdateAction = (
    name = "",
    value: unknown,
    context: string | undefined,
    onChange?: string,
    propagate = true,
    relName?: string,
): TaipyAction => ({
    type: Types.SendUpdate,
    name: name,
    context: context,
    propagate: propagate,
    payload: getPayload(value, onChange, relName),
});

export const getPayload = (value: unknown, onChange?: string, relName?: string) => {
    const ret: Record<string, unknown> = { value: value };
    if (relName) {
        ret.relvar = relName;
    }
    if (onChange) {
        ret.on_change = onChange;
    }
    return ret;
};

/**
 * Create an *action* `Action` that will be used to update `Context`.
 *
 * This action will trigger the invocation of the `on_action` Python function on the backend,
 * providing all the parameters as a payload.
 * @param name - The name of the action function on the backend.
 * @param context - The execution context.
 * @param value - The value associated with the action. This can be an object or
 *   any type of value.
 * @param args - Additional information associated to the action.
 * @returns The action fed to the reducer.
 */
export const createSendActionNameAction = (
    name: string | undefined,
    context: string | undefined,
    value: unknown,
    ...args: unknown[]
): TaipyAction => ({
    type: Types.Action,
    name: name || "",
    context: context,
    payload:
        typeof value === "object" && !Array.isArray(value) && value !== null
            ? { ...(value as object), args: args }
            : { action: value, args: args },
});

export const createRequestChartUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    context: string | undefined,
    columns: string[],
    pageKey: string,
    decimatorPayload: unknown | undefined,
): TaipyAction =>
    createRequestDataUpdateAction(
        name,
        id,
        context,
        columns,
        pageKey,
        {
            decimatorPayload: decimatorPayload,
        },
        true,
    );

export const createRequestTableUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    context: string | undefined,
    columns: string[],
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string,
    aggregates?: string[],
    applies?: Record<string, unknown>,
    styles?: Record<string, string>,
    tooltips?: Record<string, string>,
    handleNan?: boolean,
    filters?: Array<FilterDesc>,
    compare?: string,
    compareDatas?: string,
    stateContext?: Record<string, unknown>,
): TaipyAction =>
    createRequestDataUpdateAction(
        name,
        id,
        context,
        columns,
        pageKey,
        ligthenPayload({
            start: start,
            end: end,
            orderby: orderBy,
            sort: sort,
            aggregates: aggregates,
            applies: applies,
            styles: styles,
            tooltips: tooltips,
            handlenan: handleNan,
            filters: filters,
            compare: compare,
            compare_datas: compareDatas,
            state_context: stateContext,
        }),
    );

export const createRequestInfiniteTableUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    context: string | undefined,
    columns: string[],
    pageKey: string,
    start?: number,
    end?: number,
    orderBy?: string,
    sort?: string,
    aggregates?: string[],
    applies?: Record<string, unknown>,
    styles?: Record<string, string>,
    tooltips?: Record<string, string>,
    handleNan?: boolean,
    filters?: Array<FilterDesc>,
    compare?: string,
    compareDatas?: string,
    stateContext?: Record<string, unknown>,
    reverse?: boolean,
): TaipyAction =>
    createRequestDataUpdateAction(
        name,
        id,
        context,
        columns,
        pageKey,
        ligthenPayload({
            infinite: true,
            start: start,
            end: end,
            orderby: orderBy,
            sort: sort,
            aggregates: aggregates,
            applies: applies,
            styles: styles,
            tooltips: tooltips,
            handlenan: handleNan,
            filters: filters,
            compare: compare,
            compare_datas: compareDatas,
            state_context: stateContext,
            reverse: !!reverse,
        }),
    );

/**
 * Create a *request data update* `Action` that will be used to update the `Context`.
 *
 * This action will provoke the invocation of the `get_data()` method of the backend
 * library. That invocation generates an update of the elements holding the data named
 * *name* on the front-end.
 * @param name - The name of the variable holding the requested data as received as
 *   a property.
 * @param id - The identifier of the visual element.
 * @param context - The execution context.
 * @param columns - The list of the columns needed by the element that emitted this
 *   action.
 * @param pageKey - The unique identifier of the data that will be received from
 *   this action.
 * @param payload - The payload (specific to the type of component
 *  ie table, chart...).
 * @param allData - The flag indicating if all the data is requested.
 * @param library - The name of the {@link extension} library.
 * @returns The action fed to the reducer.
 */
export const createRequestDataUpdateAction = (
    name: string | undefined,
    id: string | undefined,
    context: string | undefined,
    columns: string[],
    pageKey: string,
    payload: Record<string, unknown>,
    allData = false,
    library?: string,
): TaipyAction => {
    payload = payload || {};
    if (id !== undefined) {
        payload.id = id;
    }
    payload.columns = columns;
    payload.pagekey = pageKey;
    if (library !== undefined) {
        payload.library = library;
    }
    if (allData) {
        payload.alldata = true;
    }
    return {
        type: Types.RequestDataUpdate,
        name: name || "",
        context: context,
        payload: payload,
    };
};

/**
 * Create a *request update* `Action` that will be used to update the `Context`.
 *
 * This action will generate an update of the elements holding the variables named
 * *names* on the front-end.
 * @param id - The identifier of the visual element.
 * @param context - The execution context.
 * @param names - The names of the requested variables as received in updateVarName and/or updateVars properties.
 * @param forceRefresh - Should Taipy re-evaluate the variables or use the current values
 * @returns The action fed to the reducer.
 */
export const createRequestUpdateAction = (
    id: string | undefined,
    context: string | undefined,
    names: string[],
    forceRefresh = false,
    stateContext?: Record<string, unknown>,
): TaipyAction => ({
    type: Types.RequestUpdate,
    name: "",
    context: context,
    payload: ligthenPayload({
        id: id,
        names: names,
        refresh: forceRefresh,
        state_context: stateContext,
    }),
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
    aType = aType.trim();
    if (aType) {
        aType = aType.charAt(0).toLowerCase();
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
    }
    return aType;
};

export const createAlertAction = (alert: AlertMessage): TaipyAlertAction => ({
    type: Types.SetAlert,
    atype: getAlertType(alert.atype),
    message: alert.message,
    system: alert.system,
    duration: alert.duration,
});

export const createDeleteAlertAction = (): TaipyBaseAction => ({
    type: Types.DeleteAlert,
});

export const createBlockAction = (block: BlockMessage): TaipyBlockAction => ({
    type: Types.SetBlock,
    noCancel: block.noCancel,
    action: block.action || "",
    close: !!block.close,
    message: block.message,
});

export const createNavigateAction = (
    to?: string,
    params?: Record<string, string>,
    tab?: string,
    force?: boolean,
): TaipyNavigateAction => ({
    type: Types.Navigate,
    to,
    params,
    tab,
    force,
});

export const createIdAction = (id: string): TaipyIdAction => ({
    type: Types.ClientId,
    id,
});

export const createAckAction = (id: string): TaipyAckAction => ({
    type: Types.Acknowledgement,
    id,
});

export const createDownloadAction = (dMessage?: FileDownloadProps): TaipyDownloadAction => ({
    type: Types.DownloadFile,
    content: dMessage?.content,
    name: dMessage?.name,
    onAction: dMessage?.onAction,
});

export const createSetMenuAction = (menu: MenuProps): TaipySetMenuAction => ({
    type: Types.SetMenu,
    menu,
});

export const createPartialAction = (name: string, create: boolean): TaipyPartialAction => ({
    type: Types.Partial,
    name,
    create,
});
