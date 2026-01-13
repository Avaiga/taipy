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

import axios from "axios";
import { TAIPY_CLIENT_ID } from "./wsUtils";

export const getLocalStorageValue = <T = string>(key: string, defaultValue: T, values?: T[]) => {
    const val = localStorage && (localStorage.getItem(key) as unknown as T);
    return !val ? defaultValue : !values ? val : values.indexOf(val) == -1 ? defaultValue : val;
};

export const storeClientId = (id: string) => localStorage && localStorage.setItem(TAIPY_CLIENT_ID, id);

export interface IdMessage {
    id: string;
}

export const changeFavicon = (url?: string) => {
    const link: HTMLLinkElement | null = document.querySelector("link.taipy-favicon");
    if (link) {
        const { url: taipyUrl } = link.dataset;
        const fetchUrl = url || (taipyUrl as string);
        axios
            .get(fetchUrl)
            .then(() => {
                link.href = fetchUrl;
            })
            .catch((error) => {
                if (fetchUrl !== taipyUrl) {
                    link.href = taipyUrl as string;
                }
                console.log(error);
            });
    }
};
