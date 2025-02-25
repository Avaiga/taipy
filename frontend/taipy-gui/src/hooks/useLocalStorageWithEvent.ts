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

import { Dispatch, useEffect } from "react";
import { createLocalStorageAction, TaipyBaseAction } from "../context/taipyReducers";

export const useLocalStorageWithEvent = (dispatch: Dispatch<TaipyBaseAction>, id: string) => {
    // send all localStorage data to backend on init
    useEffect(() => {
        if (localStorage && id) {
            const localStorageData: Record<string, string> = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key) {
                    localStorageData[key] = localStorage.getItem(key) || "";
                }
            }
            dispatch(createLocalStorageAction(localStorageData));
        }
    }, [dispatch, id]); // Not necessary to add dispatch to the dependency array but comply with eslint warning anyway
};
