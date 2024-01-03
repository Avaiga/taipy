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

import { createContext, Dispatch } from "react";
import { TaipyBaseAction, TaipyState } from "./taipyReducers";

/**
 * The Taipy Store.
 */
export interface TaipyStore {
    /** The State of the Taipy application. */
    state: TaipyState;
    /** The React *dispatch* function. */
    dispatch: Dispatch<TaipyBaseAction>;
}

/**
 * The Taipy-specific React context.
 *
 * The type of this variable is `React.Context<Store>`.
 */
export const TaipyContext = createContext<TaipyStore>({state: {data: {}} as TaipyState, dispatch: () => null});
TaipyContext.displayName = 'Taipy Context';

interface PageStore {
    module?: string;
}

export const PageContext = createContext<PageStore>({});
PageContext.displayName = 'Page Context';
