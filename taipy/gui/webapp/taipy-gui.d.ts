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

import { PaletteMode } from "@mui/material";
import { Theme } from "@mui/material/styles";
import { ComponentType, Dispatch, ReactNode } from "react";
import { FallbackProps } from "react-error-boundary";
import { Socket } from "socket.io-client";

export interface TaipyBaseProps {
    id?: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
    privateClassName?: string;
    children?: ReactNode;
}
export interface TaipyDynamicProps extends TaipyBaseProps {
    updateVarName?: string;
    propagate?: boolean;
    updateVars?: string;
}
export interface TaipyHoverProps {
    hoverText?: string;
    defaultHoverText?: string;
}
export interface TaipyActiveProps extends TaipyDynamicProps, TaipyHoverProps {
    active?: boolean;
    defaultActive?: boolean;
}
export interface TaipyMultiSelectProps {
    selected?: number[];
}
export interface TaipyChangeProps {
    onChange?: string;
}
/**
 * Extracts the backend name of a property.
 *
 * @param updateVars - The value held by the property *updateVars* of a component.
 * @param name - The name of a bound property.
 * @returns The backend-generated variable name.
 */
export declare const getUpdateVar: (updateVars: string, name: string) => string | undefined;
/**
 * Appends a suffix to the class names.
 *
 * @param names - The class names.
 * @param suffix - The suffix to append.
 * @returns The new list of class names.
 */
export declare const getSuffixedClassNames: (names: string | undefined, suffix: string) => string;
/**
 * An Icon representation.
 */
export interface Icon {
    /** The URL to the image. */
    path: string;
    /** The text. */
    text: string;
    /** light theme path */
    lightPath?: string;
    /** dark theme path */
    darkPath?: string;
}
/**
 * A string or an icon.
 */
export type stringIcon = string | Icon;
/**
 * An item in a List of Values (LoV).
 */
export interface LovItem {
    /** The unique identifier of this item. */
    id: string;
    /** The items label (string and/or icon). */
    item: stringIcon;
    /** The array of child items. */
    children?: LovItem[];
}
export interface MenuProps extends TaipyBaseProps {
    label?: string;
    width?: string;
    onAction?: string;
    inactiveIds?: string[];
    lov?: LovItem[];
    active?: boolean;
    selected?: string[];
    expanded?: boolean;
}
export declare const getLocalStorageValue: <T = string>(key: string, defaultValue: T, values?: T[]) => T;
export declare const storeClientId: (id: string) => void;
export interface IdMessage {
    id: string;
}
export declare const TAIPY_CLIENT_ID = "TaipyClientId";
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
export declare const sendWsMessage: (
    socket: Socket | undefined,
    type: WsMessageType,
    name: string,
    payload: Record<string, unknown> | unknown,
    id: string,
    moduleContext?: string,
    propagate?: boolean,
    serverAck?: (val: unknown) => void,
) => string;
declare enum Types {
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
    SetNotification = "SET_NOTIFICATION",
    DeleteNotification = "DELETE_NOTIFICATION",
    SetBlock = "SET_BLOCK",
    Navigate = "NAVIGATE",
    ClientId = "CLIENT_ID",
    MultipleMessages = "MULTIPLE_MESSAGES",
    SetMenu = "SET_MENU",
    DownloadFile = "DOWNLOAD_FILE",
    Partial = "PARTIAL",
    Acknowledgement = "ACKNOWLEDGEMENT",
    Broadcast = "BROADCAST",
    LocalStorage = "LOCAL_STORAGE",
    RefreshThemes = "REFRESH_THEMES",
    Patch = "PATCH",
}
interface TaipyState {
    socket?: Socket;
    isSocketConnected?: boolean;
    data: Record<string, unknown>;
    themes: Record<PaletteMode, Theme>;
    theme: Theme;
    locations: Record<string, string>;
    timeZone?: string;
    dateFormat?: string;
    dateTimeFormat?: string;
    numberFormat?: string;
    notifications: NotificationMessage[];
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
interface TaipyBaseAction {
    type: Types;
}
export interface NamePayload {
    name: string;
    payload: Record<string, unknown>;
}
export interface NotificationMessage {
    nType: string;
    message: string;
    system: boolean;
    duration: number;
    notificationId?: string;
    snackbarId: string;
}
export interface TaipyAction extends NamePayload, TaipyBaseAction {
    propagate?: boolean;
    context?: string;
}
export interface BlockMessage {
    action: string;
    noCancel: boolean;
    close: boolean;
    message: string;
}
export interface FileDownloadProps {
    content?: string;
    name?: string;
    onAction?: string;
    context?: string;
}
interface StyleKit {
    // Primary and secondary colors
    colorPrimary: string;
    colorSecondary: string;
    // Contextual color
    colorError: string;
    colorWarning: string;
    colorSuccess: string;
    // Background and elevation color for LIGHT MODE
    colorBackgroundLight: string;
    colorPaperLight: string;
    // Background and elevation color for DARK MODE
    colorBackgroundDark: string;
    colorPaperDark: string;
    // DEFINING FONTS
    // Set main font family
    fontFamily: string;
    // DEFINING ROOT STYLES
    // Set root margin
    rootMargin: string;
    // DEFINING SHAPES
    // Base border radius in px
    borderRadius: number;
    // DEFINING MUI COMPONENTS STYLES
    // Height in css size unit for inputs and buttons
    inputButtonHeight: string;
}
export interface ExtensionConfig {
    components?: string[];
    scripts?: string[];
    styles?: string[];
    loaded?: boolean;
}
export interface TaipyConfig {
    darkMode: boolean;
    themes: Record<string, Record<string, unknown>>;
    timeZone: string;
    extensions: Record<string, ExtensionConfig>;
    stylekit?: StyleKit;
    baseURL: string;
    waterMark?: string;
    rootMargin?: string;
    cssVars?: string;
    version?: string;
}

export declare const INITIAL_STATE: TaipyState;
export declare const taipyInitialize: (initialState: TaipyState, config: TaipyConfig, serverUrl?: string) => TaipyState;
export declare const initializeWebSocket: (socket: Socket | undefined, dispatch: Dispatch<TaipyBaseAction>) => void;
export declare const taipyReducer: (state: TaipyState, baseAction: TaipyBaseAction) => TaipyState;
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
export declare const createSendUpdateAction: (
    name: string | undefined,
    value: unknown,
    context: string | undefined,
    onChange?: string,
    propagate?: boolean,
    relName?: string,
) => TaipyAction;
/**
 * Create an *action* `Action` that will be used to update `Context`.
 *
 * This action will trigger the invocation of the `on_action` Python function on the backend,
 * providing all the parameters as a payload.
 * @param id - The identifier of the element that triggers the action.
 * @param module - The name of the module.
 * @param action - The name of the action callback to be triggered on the backend.
 * @param args - Additional information related to the action.
 * @returns The action fed to the reducer.
 *
 * Note: if *action* is an object, it's *action* key is used as the name of the callback function to
 * be triggered on the backend.
 *
 * The additional *args* parameters will be sent as an array in the *args* key of the payload
 * received on the backend, where each element of the array corresponds to the additional parameters
 * provided when creating the action.
 * */
export declare const createSendActionNameAction: (
    id: string | undefined,
    module: string | undefined,
    action: unknown,
    ...args: unknown[]
) => TaipyAction;
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
export declare const createRequestDataUpdateAction: (
    name: string | undefined,
    id: string | undefined,
    context: string | undefined,
    columns: string[],
    pageKey: string,
    payload: Record<string, unknown>,
    allData?: boolean,
    library?: string,
) => TaipyAction;
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
export declare const createRequestUpdateAction: (
    id: string | undefined,
    context: string | undefined,
    names: string[],
    forceRefresh?: boolean,
    stateContext?: Record<string, unknown>,
) => TaipyAction;
export declare const createRefreshThemesAction: () => TaipyBaseAction;
/**
 * A column description as received by the backend.
 */
export interface ColumnDesc {
    /** The unique column identifier. */
    dfid: string;
    /** The column type. */
    type: string;
    /** The value format. */
    format?: string;
    /** The column title. */
    title?: string;
    /** The order of the column. */
    index: number;
    /** The column width. */
    width?: number | string;
    /** If true, the column cannot be edited. */
    notEditable?: boolean;
    /** The name of the column that holds the CSS className to
     *  apply to the cells. */
    className?: string;
    /** The name of the column that holds the tooltip to
     *  show on the cells. */
    tooltip?: string;
    /** The name of the column that holds the formatted value to
     *  show on the cells. */
    formatFn?: string;
    /** The value that would replace a NaN value. */
    nanValue?: string;
    /** The TimeZone identifier used if the type is `date`. */
    tz?: string;
    /** The flag that allows filtering. */
    filter?: boolean;
    /** The name of the aggregation function. */
    apply?: string;
    /** The flag that allows the user to aggregate the column. */
    groupBy?: boolean;
    widthHint?: number;
    /** The list of values that can be used on edit. */
    lov?: string[];
    /** If true the user can enter any value besides the lov values. */
    freeLov?: boolean;
    /** If false, the column cannot be sorted */
    sortable?: boolean;
    /** The column headers if more than one. */
    headers?: string[];
    /** The index of the multi index if exists. */
    multi?: number;
    /** If true or not set, line breaks are transformed into <BR>. */
    lineBreak?: boolean;
}
/**
 * A cell value type.
 */
export type RowValue = string | number | boolean | null;
/**
 * The definition of a table row.
 *
 * A row definition associates a name (a string) to a type (a {@link RowValue}).
 */
export type RowType = Record<string, RowValue>;
export type TableValueType = Record<string, Record<string, any>>;
export interface TaipyTableProps extends TaipyActiveProps, TaipyMultiSelectProps {
    data?: TableValueType;
    columns?: string;
    defaultColumns: string;
    height?: string;
    width?: string;
    pageSize?: number;
    onEdit?: string;
    onDelete?: string;
    onAdd?: string;
    onAction?: string;
    editable?: boolean;
    defaultEditable?: boolean;
    rowClassName?: string;
    tooltip?: string;
    cellTooltip?: string;
    nanValue?: string;
    filter?: boolean;
    size?: "small" | "medium";
    defaultKey?: string;
    userData?: unknown;
    downloadable?: boolean;
    onCompare?: string;
    compare?: boolean;
    useCheckbox?: boolean;
    sortable?: boolean;
}
export interface TaipyPaginatedTableProps extends TaipyTableProps {
    pageSizeOptions?: string;
    allowAllRows?: boolean;
    showAll?: boolean;
}
export interface FilterDesc {
    col: string;
    action: string;
    value: string | number | boolean | Date;
    type: string;
    matchcase?: boolean;
    params?: number[];
}
export interface ChartProp extends TaipyActiveProps, TaipyChangeProps {
    title?: string;
    defaultTitle?: string;
    width?: string | number;
    height?: string | number;
    config?: string;
    defaultConfig: string;
    data?: Record<string, TraceValueType>;
    animationData?: Record<string, TraceValueType>;
    layout?: string;
    defaultLayout?: string;
    plotConfig?: string;
    onRangeChange?: string;
    render?: boolean;
    defaultRender?: boolean;
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
    figure?: string;
    onClick?: string;
    dataVarNames?: string;
}
export type TraceValueType = Record<string, (string | number)[]>;
export declare const Chart: (props: ChartProp) => import("react/jsx-runtime").JSX.Element | null;
export interface DialogProps extends TaipyActiveProps {
    title: string;
    onAction?: string;
    closeLabel?: string;
    labels?: string;
    page?: string;
    partial?: boolean;
    open?: boolean;
    defaultOpen?: string | boolean;
    children?: ReactNode;
    height?: string | number;
    width?: string | number;
    localAction?: (idx: number) => void;
    refId?: string;
    defaultRefId?: string;
    popup?: boolean;
}
export declare const Dialog: (props: DialogProps) => import("react/jsx-runtime").JSX.Element;
export interface FileSelectorProps extends TaipyActiveProps {
    onAction?: string;
    label?: string;
    defaultLabel?: string;
    multiple?: boolean;
    selectionType?: string;
    extensions?: string;
    dropMessage?: string;
    notify?: boolean;
    width?: string | number;
    icon?: ReactNode;
    withBorder?: boolean;
    onUploadAction?: string;
    uploadData?: string;
}
export declare const FileSelector: (props: FileSelectorProps) => import("react/jsx-runtime").JSX.Element;
export interface LoginProps extends TaipyBaseProps {
    title?: string;
    onAction?: string;
    message?: string;
    defaultMessage?: string;
    labels?: string;
}
export declare const Login: (props: LoginProps) => import("react/jsx-runtime").JSX.Element;

export declare const Router = () => import("react/jsx-runtime").JSX.Element;
export interface TableProps extends TaipyPaginatedTableProps {
    autoLoading?: boolean;
}
export declare const Table: ({ autoLoading, ...rest }: TableProps) => import("react/jsx-runtime").JSX.Element;
export interface FilterColumnDesc extends ColumnDesc {
    params?: number[];
}
export interface TableFilterProps {
    fieldHeader?: string;
    fieldHeaderTooltip?: string;
    columns: Record<string, FilterColumnDesc>;
    colsOrder?: Array<string>;
    onValidate: (data: Array<FilterDesc>) => void;
    appliedFilters?: Array<FilterDesc>;
    className?: string;
    filteredCount: number;
}
export declare const TableFilter: (props: TableFilterProps) => import("react/jsx-runtime").JSX.Element;
export interface SortDesc {
    col: string;
    order: boolean;
    params?: number[];
}
export interface SortColumnDesc extends ColumnDesc {
    params?: number[];
}
export interface TableSortProps {
    fieldHeader?: string;
    fieldHeaderTooltip?: string;
    columns: Record<string, SortColumnDesc>;
    colsOrder?: Array<string>;
    onValidate: (data: Array<SortDesc>) => void;
    appliedSorts?: Array<SortDesc>;
    className?: string;
}
export declare const TableSort: (props: TableSortProps) => import("react/jsx-runtime").JSX.Element;
/**
 * A function that retrieves the dynamic className associated
 * to an instance of component through the style property
 *
 * @param children - The react children of the component
 * @returns The associated className.
 */
export declare const getComponentClassName: (children: ReactNode) => string;
export interface MetricProps extends TaipyBaseProps, TaipyHoverProps {
    value?: number;
    defaultValue?: number;
    delta?: number;
    defaultDelta?: number;
    type?: string;
    min?: number;
    max?: number;
    deltaColor?: string;
    negativeDeltaColor?: string;
    threshold?: number;
    defaultThreshold?: number;
    format?: string;
    deltaFormat?: string;
    barColor?: string;
    showValue?: boolean;
    colorMap?: string;
    title?: string;
    layout?: string;
    defaultLayout?: string;
    width?: string | number;
    height?: string | number;
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
}
export declare const Metric: (props: MetricProps) => import("react/jsx-runtime").JSX.Element;
/**
 * A LoV (list of value) element.
 *
 * Each `LoVElt` holds:
 *
 * - Its identifier as a string;
 * - Its label (or icon) as a `stringIcon`;
 * - Potential child elements as an array of `LoVElt`s.
 */
export type LoVElt = [string, stringIcon, LoVElt[]?];
/**
 * A series of LoV elements.
 */
export type LoV = LoVElt[];
/**
 * A React hook that returns a LoV list from the LoV default value and the LoV bound value.
 * @param lov - The bound lov value.
 * @param defaultLov - The JSON-stringified default LoV value.
 * @param tree - This flag indicates if the LoV list is a tree or a flat list (default is false).
 * @returns A list of LoV items.
 */
export declare const useLovListMemo: (lov: LoV | undefined, defaultLov: string, tree?: boolean) => LovItem[];
interface TaipyStore {
    /** The State of the Taipy application. */
    state: TaipyState;
    /** The React *dispatch* function. */
    dispatch: Dispatch<TaipyBaseAction>;
    /** The URL of the Taipy server. */
    serverUrl?: string;
    /** The Taipy configuration. */
    config?: TaipyConfig;
    /** The Taipy version. */
    version?: string;
}
/**
 * The Taipy-specific React context.
 *
 * The type of this variable is `React.Context<Store>`.
 */
export declare const TaipyContext: import("react").Context<TaipyStore>;
export interface PageStore {
    module?: string;
}
export declare const PageContext: import("react").Context<PageStore>;
/**
 * A React hook that provides actions for updating data and triggering backend functions.
 *
 * The `sendUpdate` function allows to update a variable on the backend and trigger the `on_change`
 * callback.<br/>
 * The `sendAction` function allows to trigger an `on_action` callback on the backend with a custom
 * payload.
 *
 * @returns An object containing the following keys:
 * - *sendUpdate* is a function that can be used to update a variable on the backend and trigger the
 *   `on_change` callback. It takes the following parameters:
 *   - *name*: The name of the variable to update on the backend.
 *   - *value*: The new value for the variable.
 *   - *onChange*: The name of the `on_change` callback function to trigger.</br>
 *     If not provided, the default `on_change` callback will be triggered if it exists.
 *   - *propagate*: Whether to propagate the update to other components.
 *   - *relName*: The name of the related variable (used when the variable is a value in a list of
 *     values).
 * - *sendAction* is a function that can be used to trigger a backend callback with a custom payload.
 *   This function takes the following parameters:
 *   - *action*: The name of the callback function to trigger on the backend.</br>
 *     If not provided, the default `on_action` callback will be triggered if it exists.
 *   - *args*: Additional arguments sent to the backend in the `payload.args` array of the callback
 *     function.
 */
export declare function useActions(): {
    sendAction: (id: string | undefined, action: string | undefined, ...args: unknown[]) => void;
    sendUpdate: (
        name: string | undefined,
        value: unknown,
        onChange?: string,
        propagate?: boolean,
        relName?: string,
    ) => void;
};
/**
 * A React hook that requests an update from the backend for every dynamic property of the element
 * on its first render.
 *
 * @param id - The identifier of the element.
 * @param updateVars - The content of the property *updateVars* of the component.
 * @param varName - The default property backend provided variable (typically the *updateVarName*
 *        property of the component).
 * @param forceRefresh - If true, Taipy re-evaluates the variables. If false, it uses the current values.
 */
export declare function useRequestUpdateOnFirstRender(
    id?: string,
    updateVars?: string,
    varName?: string,
    forceRefresh?: boolean,
): void;
/**
 * A React hook to manage a dynamic scalar property.
 *
 * A dynamic scalar property  is defined by a default property and a bound property.
 * @typeParam T - The dynamic property type.
 * @param value - The bound value.
 * @param defaultValue - The default value.
 * @param defaultStatic - The default static value.
 * @returns The latest updated value.
 */
export declare const useDynamicProperty: <T>(
    value: T,
    defaultValue: T,
    defaultStatic: T,
    checkType?: string,
    nullToDefault?: boolean,
) => T;
/**
 * A React hook to manage a dynamic dict property (prev. useDynamicJsonProperty).
 *
 * A dynamic dict property  is defined by a default property and a bound property.
 * @typeParam T - The dynamic property type.
 * @param value - The bound value.
 * @param defaultValue - The default value.
 * @param defaultStatic - The default static value.
 * @returns The latest updated value.
 */
export declare const useDynamicDictProperty: <T>(
    value: string | undefined,
    defaultValue: string,
    defaultStatic: T,
) => T;
/**
 * A React hook that requests an update for every dynamic property of the element.
 * @param dispatch - The React dispatcher associated to `TaipyContext`.
 * @param id - The identifier of the element.
 * @param context - The execution context.
 * @param updateVars - The content of the property `updateVars`.
 * @param varName - The default property backend provided variable (through property `updateVarName`).
 * @param forceRefresh - Should Taipy re-evaluate the variables or use the current values.
 */
export declare const useDispatchRequestUpdateOnFirstRender: (
    dispatch: Dispatch<TaipyBaseAction>,
    id?: string,
    context?: string,
    updateVars?: string,
    varName?: string,
    forceRefresh?: boolean,
) => void;
/**
 * A React hook that returns the *dispatch* function.
 *
 * The *dispatch* function allows to send Actions to the Store and initiate backend\
 * communications.
 * @returns The *dispatch* function.
 */
export declare const useDispatch: () => Dispatch<TaipyBaseAction>;
/**
 * A React hook that returns the page module.
 *
 * The *module* Needs to be added to all Actions to allow for the correct execution of backend functions.
 * @returns The page module.
 */
export declare const useModule: () => string | undefined;
/**
 * A React hook to manage classNames (dynamic and static).
 * cf. useDynamicProperty
 *
 * @param libClassName - The default static className.
 * @param dynamicClassName - The bound className.
 * @param className - The default user set className.
 * @returns The complete list of applicable classNames.
 */
export declare const useClassNames: (libClassName?: string, dynamicClassName?: string, className?: string) => string;
export declare const uploadFile: (
    varName: string,
    context: string | undefined,
    onAction: string | undefined,
    uploadData: string | undefined,
    files: FileList,
    progressCallback: (val: number) => void,
    id: string,
    uploadUrl?: string,
) => Promise<string>;
export declare const emptyArray: never[];
export declare const ErrorFallback: (props: FallbackProps) => import("react/jsx-runtime").JSX.Element;
export declare const getRegisteredComponents: (extensions?: Record<string, ExtensionConfig>) => Record<string, ComponentType<unknown>>;
export declare const unregisteredRender: (tagName?: string, error?: string) => import("react/jsx-runtime").JSX.Element;
export declare const renderError: (props: { error: string }) => import("react/jsx-runtime").JSX.Element;

export { TaipyBaseAction as Action, TaipyContext as Context, TaipyState as State, TaipyStore as Store };

export {};
