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

import { Type } from "apache-arrow";

export enum DataFormat {
    JSON = "JSON",
    APACHE_ARROW = "ARROW",
}

const coerceBigInt = (val: unknown) => {
    if (typeof val == "bigint") {
        try {
            val = Number(val);
        } catch (e) {
            console.warn("Cannot coerce bigint value to number", val, e);
        }
    }
    return val;
}

export const parseData = (data: Record<string, unknown>): Promise<Record<string, unknown>> => {
    if (data?.format === DataFormat.APACHE_ARROW) {
        const multi = typeof data.multi === "boolean" && data.multi;
        const orient = data.orient;
        const pData = multi ? (data.data as Array<unknown>) : [data.data];
        return new Promise((resolve, reject) => {
            import("apache-arrow").then(({tableFromIPC}) => {
                const res = pData.map((d) => {
                    const arrowData = tableFromIPC(new Uint8Array(d as ArrayBuffer));
                    const tableHeading = arrowData.schema.fields.map((f) => f.name);
                    if (orient === "records") {
                        const convertedData: Array<unknown> = [];
                        for (const row of arrowData) {
                            const dataRow: Record<string, unknown> = {};
                            for (const cell of row) {
                                dataRow[cell[0]] = coerceBigInt(cell[1]);
                            }
                            convertedData.push(dataRow);
                        }
                        return convertedData;
                    } else if (orient === "list") {
                        const convertedData: Record<string, unknown> = {};
                        for (let i = 0; i < tableHeading.length; i++) {
                            const col = arrowData.getChildAt(i);
                            convertedData[tableHeading[i]] = col?.type.typeId === Type.Int ? Array.from(col).map(coerceBigInt) : col?.toArray();
                        }
                        return convertedData;
                    }
                });
                if (typeof data.dataExtraction === "boolean" && data.dataExtraction) {
                    data = (multi ? res : res[0]) as Record<string, unknown>;
                } else {
                    data.data = multi ? res : res[0];
                }
                resolve(data);
            }).catch(reject);
        });
    } else if (typeof data?.dataExtraction === "boolean" && data.dataExtraction) {
        data = data.data as Record<string, unknown>;
    }
    return new Promise((resolve) => {
        resolve(data);
    });
};
