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

import * as React from "react";

/**
 * Extracts the backend name of a property.
 *
 * @param updateVars - The value held by the property *updateVars*.
 * @param name - The name of a bound property.
 * @returns The backend-generated variable name.
 */
export declare const getUpdateVar: (updateVars: string, name: string) => string | undefined;

export interface TaipyActiveProps extends TaipyDynamicProps, TaipyHoverProps {
    defaultActive?: boolean;
    active?: boolean;
}
export interface TaipyHoverProps {
    hoverText?: string;
    defaultHoverText?: string;
}
export interface TaipyDynamicProps extends TaipyBaseProps {
    updateVarName?: string;
    propagate?: boolean;
    updateVars?: string;
}
export interface TaipyBaseProps {
    id?: string;
    libClassName?: string;
    className?: string;
    dynamicClassName?: string;
}
export interface DialogProps extends TaipyActiveProps {
    title: string;
    onAction?: string;
    closeLabel?: string;
    labels?: string;
    page?: string;
    partial?: boolean;
    open?: boolean;
    defaultOpen?: string | boolean;
    children?: React.ReactNode;
    height?: string | number;
    width?: string | number;
    localAction?: (idx: number) => void;
}
export declare const Dialog: (props: DialogProps) => JSX.Element;

export interface ChartProp extends TaipyActiveProps, TaipyChangeProps {
    title?: string;
    width?: string | number;
    height?: string | number;
    defaultConfig: string;
    config?: string;
    data?: Record<string, TraceValueType>;
    defaultLayout?: string;
    layout?: string;
    plotConfig?: string;
    onRangeChange?: string;
    testId?: string;
    render?: boolean;
    defaultRender?: boolean;
    template?: string;
    template_Dark_?: string;
    template_Light_?: string;
}
export type TraceValueType = Record<string, (string | number)[]>;
export declare const Chart: (props: ChartProp) => JSX.Element;

export interface TaipyMultiSelectProps {
    selected?: number[];
}
export interface TaipyChangeProps {
    onChange?: string;
}

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
    lineStyle?: string;
    tooltip?: string;
    cellTooltip?: string;
    nanValue?: string;
    filter?: boolean;
    size?: "small" | "medium";
    userData?: unknown;
}
export interface TaipyPaginatedTableProps extends TaipyTableProps {
    pageSizeOptions?: string;
    allowAllRows?: boolean;
    showAll?: boolean;
}
export interface TableProps extends TaipyPaginatedTableProps {
    autoLoading?: boolean;
}
export declare const Table: (props: TableProps) => JSX.Element;

export declare const Router: () => JSX.Element;

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
export declare type stringIcon = string | Icon;
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
/**
 * A LoV (list of value) element.
 *
 * Each `LoVElt` holds:
 *
 * - Its identifier as a string;
 * - Its label (or icon) as a `stringIcon`;
 * - Potential child elements as an array of `LoVElt`s.
 */
export declare type LoVElt = [
    /** The identifier. */
    string,
    /** The label or icon. */
    stringIcon,
    /** The list of children. */
    LoVElt[]?
];
/**
 * A series of LoV elements.
 */
export declare type LoV = LoVElt[];
/**
 * A React hook that returns a LoV list from the LoV default value and the LoV bound value.
 * @param lov - The bound lov value.
 * @param defaultLov - The JSON-stringified default LoV value.
 * @param tree - This flag indicates if the LoV list is a tree or a flat list (default is false).
 * @returns A list of LoV items.
 */
export declare const useLovListMemo: (lov: LoV | undefined, defaultLov: string, tree?: boolean) => LovItem[];
/**
 * The state of the underlying Taipy application.
 */
export interface State {}
/**
 * Application actions as used by the application reducer.
 */
export interface Action {}
/**
 * Create a *send update* `Action` that will be used to update `Context`.
 *
 * This action will update the variable *name* (if *propagate* is true) and trigger the
 * invocation of the `on_change` Python function on the backend.
 * @param name - The name of the variable holding the requested data
 *    as received as a property.
 * @param value - The new value for the variable named *name*.
 * @param context - The execution context (property `context`).
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
    relName?: string
) => Action;
/**
 * Create an *action* `Action` that will be used to update `Context`.
 *
 * This action will trigger the invocation of the `on_action` Python function on the backend,
 * providing all the parameters as a payload.
 * @param name - The name of the action function on the backend.
 * @param context - The execution context (property `context`).
 * @param value - The value associated with the action. This can be an object or
 *   any type of value.
 * @param args - Additional information associated to the action.
 * @returns The action fed to the reducer.
 */
export declare const createSendActionNameAction: (
    name: string | undefined,
    context: string | undefined,
    value: unknown,
    ...args: unknown[]
) => Action;
/**
 * Create a *request data update* `Action` that will be used to update the `Context`.
 *
 * This action will provoke the invocation of the `get_data()` method of the backend
 * library. That invocation generates an update of the elements holding the data named
 * *name* on the frontend.
 * @param name - The name of the variable holding the requested data as received as
 *   a property.
 * @param id - The identifier of the visual element.
 * @param context - The execution context (property `context`).
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
    library?: string
) => Action;
/**
 * Create a *request update* `Action` that will be used to update the `Context`.
 *
 * This action will generate an update of the elements holding the variables named
 * *names* on the front-end.
 * @param id - The identifier of the visual element.
 * @param context - The execution context (property `context`).
 * @param names - The names of the requested variables as received in updateVarName and/or updateVars properties.
 * @param forceRefresh - Should Taipy re-evaluate the variables or use the current values.
 * @returns The action fed to the reducer.
 */
export declare const createRequestUpdateAction: (
    id: string | undefined,
    context: string | undefined,
    names: string[],
    forceRefresh?: boolean
) => Action;
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
    /** The width. */
    width?: number | string;
    /** If set to true, the column should not be editable. */
    notEditable?: boolean;
    /** The column name that would hold the css classname to apply to the cell. */
    style?: string;
    /** The value that would replace a NaN value. */
    nanValue?: string;
    /** The TimeZone identifier used if the type is Date. */
    tz?: string;
    /** The flag that allows filtering. */
    filter?: boolean;
    /** The identifier for the aggregation function. */
    apply?: string;
    /** The flag that would allow the user to aggregate the column. */
    groupBy?: boolean;
    widthHint?: number;
}
/**
 * A cell value type.
 */
export declare type RowValue = string | number | boolean | null;
/**
 * The definition of a table row.
 *
 * A row definition associates a name (a string) to a type (a {@link RowValue}).
 */
export declare type RowType = Record<string, RowValue>;
/**
 * The Taipy Store.
 */
export interface Store {
    /** The State of the Taipy application. */
    state: State;
    /** The React *dispatch* function. */
    dispatch: React.Dispatch<Action>;
}
/**
 * The Taipy-specific React context.
 *
 * The type of this variable is `React.Context<Store>`.
 */
export declare const Context: React.Context<Store>;
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
export declare const useDynamicProperty: <T>(value: T, defaultValue: T, defaultStatic: T) => T;
/**
 * A React hook to manage a dynamic json property.
 *
 * A dynamic scalar property  is defined by a default property and a bound property.
 * @typeParam T - The dynamic property type.
 * @param value - The bound value.
 * @param defaultValue - The default value.
 * @param defaultStatic - The default static value.
 * @returns The latest updated value.
 */
export const useDynamicJsonProperty: <T>(value: string | T, defaultValue: string, defaultStatic: T) => T;
/**
 * A React hook that requests an update for every dynamic property of the element.
 * @param dispatch - The React dispatcher associated to `TaipyContext`.
 * @param id - The identifier of the element.
 * @param context - The execution context (property `context`).
 * @param updateVars - The content of the property `updateVars`.
 * @param varName - The default property backend provided variable (through property `updateVarName`).
 * @param forceRefresh - Should Taipy re-evaluate the variables or use the current values.
 */
export declare const useDispatchRequestUpdateOnFirstRender: (
    dispatch: React.Dispatch<Action>,
    id?: string,
    context?: string,
    updateVars?: string,
    varName?: string,
    forceRefresh?: boolean
) => void;
/**
 * A React hook that returns the *dispatch* function.
 *
 * The *dispatch* function allows to send Actions to the Store and initiate backend\
 * communications.
 * @returns The *dispatch* function.
 */
export declare const useDispatch: () => React.Dispatch<Action>;
/**
 * A React hook that returns the page module.
 *
 * The *module* Needs to be added to all Actions to allow for the correct execution of backend functions.
 * @returns The page module.
 */
export declare const useModule: () => string | undefined;
