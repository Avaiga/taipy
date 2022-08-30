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

export interface TaipyState {
}
export interface TaipyBaseAction {
}
export interface TaipyStore {
    state: TaipyState;
    dispatch: import("react").Dispatch<TaipyBaseAction>;
}
export declare const TaipyContext: import("react").Context<TaipyStore>;

// utils
export declare const useDynamicProperty: <T>(value: T, defaultValue: T, defaultStatic: T) => T;

// Reducers
export declare const createSendActionNameAction: (name: string | undefined, value: unknown, ...args: unknown[]) => TaipyBaseAction;
export declare const createSendUpdateAction: (name: string | undefined, value: unknown, onChange?: string, propagate?: boolean, relName?: string) => TaipyBaseAction;
export declare const createRequestDataUpdateAction: (name: string | undefined, id: string | undefined, columns: string[], pageKey: string, payload: Record<string, unknown>, allData?: boolean, library?: string) => TaipyBaseAction;


//Comps
export declare const Router: () => JSX.Element;

//lov
export declare type LoVElt = [
    string,
    stringIcon,
    LoVElt[]?
];
export declare type LoV = LoVElt[];
export interface Icon {
    path: string;
    text: string;
}
export declare type stringIcon = string | Icon;
export interface LovItem {
    id: string;
    item: stringIcon;
    children?: LovItem[];
}
export declare const getUpdateVar: (updateVars: string, name: string) => string | undefined;
export declare const useLovListMemo: (lov: LoV | undefined, defaultLov: string, tree?: boolean) => LovItem[];
export declare const useDispatchRequestUpdateOnFirstRender: (dispatch: import("react").Dispatch<TaipyBaseAction>, id?: string, updateVars?: string, varName?: string) => void;


// tabular data
export interface ColumnDesc {
    dfid: string;
    type: string;
    format: string;
    title?: string;
    index: number;
    width?: number | string;
    notEditable?: boolean;
    style?: string;
    nanValue?: string;
    tz?: string;
    filter?: boolean;
    apply?: string;
    groupBy?: boolean;
    widthHint?: number;
}
export declare type RowValue = string | number | null;
export declare type RowType = Record<string, RowValue>;
