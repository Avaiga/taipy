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

import { createContext, Dispatch } from "react";
import { TaipyBaseAction, TaipyState } from "./taipyReducers";

/**
 * The Taipy Store.
 */
export interface TaipyStore {
    /** {TaipyState} The State of the Taipy Application. */
    state: TaipyState;
    /** {React.Dispatch<TaipyAction>} The react dispatch function. */
    dispatch: Dispatch<TaipyBaseAction>;
}

/**
 * {React.Context} Taipy specific react context.
 */
export const TaipyContext = createContext<TaipyStore>({state: {data: {}} as TaipyState, dispatch: () => null});
TaipyContext.displayName = 'Taipy Context';
