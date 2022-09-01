/*
 * Copyright 2022 Avaiga Private Limited
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

/**
 * This extracts the backend name of a given property identified by `name`.
 * @param {string} updateVars - The value held by the property `updateVars`.
 * @param {string} name - The name of a bound property.
 * @returns {string | undefined} The backend generated variable name.
 */
export declare const getUpdateVar: (updateVars: string, name: string) => string | undefined;

export declare const Router: () => JSX.Element;

/**
 * An Icon representation.
 */
export interface Icon {
    /** {string} The URL to the image. */
    path: string;
    /** {string} The text. */
    text: string;
}
/**
 * A String or icon.
 */
export declare type stringIcon = string | Icon;
/**
 * An item of lov.
 */
export interface LovItem {
    /** {string} The unique identifier. */
    id: string;
    /** {StringIcon} The label (string and/or icon). */
    item: stringIcon;
    /** {LovItem[] | undefined} The optional array of children. */
    children?: LovItem[];
}
/**
 * A lov element.
 */
export declare type LoVElt = [
    /** {string} The identifier. */
    string,
    /** {stringIcon} The label. */
    stringIcon,
    /** {LoVElt[] | undefined} The optional list of children. */
    LoVElt[]?
];
/**
 * The list of lov elements.
 */
export declare type LoV = LoVElt[];
/**
 * This React hook returns a lov list from the lov default value and the lov bound value.
 * @param {LoV | undefined} lov - The bound lov value.
 * @param {string} defaultLov - The json stringify default lov value.
 * @param {boolean | undefined} [tree] - This flag indicates if the LoV list is a tree or a flat list (default is false).
 * @returns {LovItem[]} A list of items.
 */
export declare const useLovListMemo: (lov: LoV | undefined, defaultLov: string, tree?: boolean) => LovItem[];
/**
 * TaipyState The State of the Taipy Application.
 */
 export interface TaipyState {}
 /**
 * TaipyAction The object used by the reducer.
 */
export interface TaipyAction {
}
/**
 * Creates a `TaipyAction` that will be used to update `TaipyContext`.
 * This action will update the variable `name` (if `propagate` === true) and provoke the invocation of the on_change python function on the backend.
 * @param {string | undefined} [name] - The name of the variable holding the requested data as received as a property (default is "").
 * @param {unknown} value - The new value for the variable named `name`.
 * @param {string | undefined} onChange - The name of the on_change python function to invoke on the backend (default to "on_change" on the backend).
 * @param {boolean | undefined} [propagate] - A flag indicating that the variable should be automatically updated on the backend (default is true).
 * @param {string | undefined} [relName] - The name of the optional related variable (for example the lov when a lov value is updated).
 * @returns {TaipyAction} The action fed to the reducer.
 */
 export declare const createSendUpdateAction: (name: string | undefined, value: unknown, onChange?: string, propagate?: boolean, relName?: string) => TaipyAction;
 /**
  * Creates a `TaipyAction` that will be used to update `TaipyContext`.
  * This action will provoke the invocation of an on_action python function on the backend with all parameters as a payload.
  * @param {string | undefined} name - The name of the backend action.
  * @param {unknown} value - The value associated with the action, this can be an object or any type of value.
  * @param {unknown[]} args - Additional informations associated to the action.
  * @returns {TaipyAction}  The action fed to the reducer.
  */
 export declare const createSendActionNameAction: (name: string | undefined, value: unknown, ...args: unknown[]) => TaipyAction;
 /**
  * Creates a `TaipyAction` that will be used to update `TaipyContext`.
  * This action will provoke the invocation of the get_data python function on the backend that will generate an update of the elements holding data named `name` on the frontend.
  * @param {string} name - The name of the variable holding the requested data as received as a property.
  * @param {string | undefined} id - The id of the visual element.
  * @param {string[]} columns - The list of the columns needed by the element emitting this action.
  * @param {string} pageKey - The unique identifier to the data that will be received from this action.
  * @param {Record<string, unknown>} payload - The payload (specific to the type of component ie table, chart ...).
  * @param {boolean | undefined} [allData] - The flag indicating if all the data is requested (default is false).
  * @param {string | undefined} library - The optional name of the library {@link extension}.
  * @returns {TaipyAction} The action fed to the reducer.
  */
 export declare const createRequestDataUpdateAction: (name: string | undefined, id: string | undefined, columns: string[], pageKey: string, payload: Record<string, unknown>, allData?: boolean, library?: string) => TaipyAction;
 /**
  * The Column description as received by the backend.
  */
 export interface ColumnDesc {
     /** {string} The unique column identifier. */
     dfid: string;
     /** {string} The column type. */
     type: string;
     /** {string} The optional value format. */
     format?: string;
     /** {string | undefined} The optional column title. */
     title?: string;
     /** {number} The order of the column. */
     index: number;
     /** {number | string | undefined} The optional width. */
     width?: number | string;
     /** {boolean | undefined} If set to true, the column should not be editable. */
     notEditable?: boolean;
     /** {string | undefined} The optional column name that would hold the css classname to apply to the cell. */
     style?: string;
     /** {string | undefined} The optional value that would replace a NaN value. */
     nanValue?: string;
     /** {string | undefined} The optional TimeZone identifier used if the type is Date. */
     tz?: string;
     /** {boolean | undefined} The flag that allows filtering. */
     filter?: boolean;
     /** {string | undefined} The optional identifier for the aggregation function. */
     apply?: string;
     /** {boolean | undefined} The optional flag that would allow the user to aggregate the column. */
     groupBy?: boolean;
     widthHint?: number;
 }
 /**
  * A cell value type.
  */
 export declare type RowValue = string | number | boolean | null;
 /**
  * The row definition composed of a key/value string/`RowValue`.
  */
 export declare type RowType = Record<string, RowValue>;
 /**
  * The Taipy Store.
  */
 export interface TaipyStore {
     /** {TaipyState} The State of the Taipy Application. */
     state: TaipyState;
     /** {React.Dispatch<TaipyAction>} The react dispatch function. */
     dispatch: import("react").Dispatch<TaipyAction>;
 }
 /**
  * {React.Context<TaipyStore>} Taipy specific react context.
  */
 export declare const TaipyContext: import("react").Context<TaipyStore>;
 /**
  * This react hook helps manage a dynamic scalar property (defined by a default property and a bound property).
  * @typeparam T - The dynamic property type.
  * @param {T} value - The bound value
  * @param {T} defaultValue - The default value
  * @param {T} defaultStatic - The default static value
  * @returns {T} The latest updated value.
  */
 export declare const useDynamicProperty: <T>(value: T, defaultValue: T, defaultStatic: T) => T;
 /**
  * This React hook requests an update for every dynamic property of the element.
  * @param {React.Dispatch} dispatch - The react dispatcher associated to `TaipyContext`.
  * @param {string | undefined} id - The optional id of the element.
  * @param {string} updateVars - The content of the property `updateVars`.
  * @param {string | undefined} varName - The default property backend provided variable (through property `updateVarName`).
  */
 export declare const useDispatchRequestUpdateOnFirstRender: (dispatch: import("react").Dispatch<TaipyAction>, id?: string, updateVars?: string, varName?: string) => void;
