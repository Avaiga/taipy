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

export interface PatchChange {
    [key: string | number]: string | number | boolean | null | PatchChange;
}
export interface PatchRemove {
    [key: string | number]: null | PatchRemove;
}

const RE_NUMBER = /^-?\d+$/;

export const patchValue = <T>(toBePatched: T, change?: PatchChange, remove?: PatchRemove): T => {
    let patchedValue = toBePatched;
    if (change) {
        // Apply changes
        Object.entries(change).forEach(([k, v]) => {
            const sIdx = Number(k);
            const idx = sIdx < 0 ? -1 - sIdx : sIdx;
            const insert = sIdx < 0;
            if (
                Array.isArray(toBePatched) &&
                RE_NUMBER.test(k) &&
                (insert ? toBePatched.length > idx : toBePatched.length >= idx)
            ) {
                // TODO deal with _tp_index
                const oldValue = toBePatched[idx];
                if (oldValue !== v) {
                    if (Array.isArray(v) && v.length > 0) {
                        if (insert) {
                            if (idx >= (patchedValue as Array<unknown>).length) {
                                patchedValue = [...(patchedValue as Array<unknown>), ...v] as T;
                            } else {
                                if (patchedValue === toBePatched) {
                                    patchedValue = [...toBePatched] as T;
                                }
                                (patchedValue as Array<unknown>).splice(idx, 0, ...v);
                            }
                        } else {
                            if (patchedValue === toBePatched) {
                                patchedValue = [...toBePatched] as T;
                            }
                            const newArray = (v as Array<unknown>).map((item, j) => {
                                const oldItem = (toBePatched as Array<unknown>)[idx + j];
                                if (
                                    typeof item === "object" &&
                                    item !== null &&
                                    typeof oldItem === "object" &&
                                    oldItem !== null
                                ) {
                                    return patchValue(oldItem, item as PatchChange);
                                } else {
                                    return item;
                                }
                            });
                            (patchedValue as Array<unknown>).splice(idx, newArray.length, ...newArray);
                        }
                    } else if (
                        oldValue !== null &&
                        typeof oldValue === "object" &&
                        v !== null &&
                        typeof v === "object"
                    ) {
                        const newValue = patchValue(oldValue, v);
                        if (newValue !== oldValue) {
                            if (patchedValue === toBePatched) {
                                patchedValue = [...toBePatched] as T;
                            }
                            (patchedValue as Array<unknown>)[idx] = newValue;
                        }
                    } else if (
                        (oldValue === null || typeof oldValue !== "object") &&
                        (v === null || typeof v !== "object")
                    ) {
                        if (idx >= (patchedValue as Array<unknown>).length) {
                            patchedValue = [...(patchedValue as Array<unknown>), v] as T;
                        } else {
                            if (patchedValue === toBePatched) {
                                patchedValue = [...toBePatched] as T;
                            }
                            (patchedValue as Array<unknown>)[idx] = v;
                        }
                    }
                }
            } else if (toBePatched && typeof toBePatched === "object" && !Array.isArray(toBePatched)) {
                const oldValue = (toBePatched as Record<string, unknown>)[k];
                if (oldValue !== v) {
                    if (Array.isArray(v) && v.length > 0) {
                        if (patchedValue === toBePatched) {
                            patchedValue = { ...toBePatched };
                        }
                        (patchedValue as Record<string, unknown>)[k] = v;
                    } else if (
                        oldValue !== null &&
                        typeof oldValue === "object" &&
                        v !== null &&
                        typeof v === "object"
                    ) {
                        const newValue = patchValue(oldValue, v);
                        if (newValue !== oldValue) {
                            if (patchedValue === toBePatched) {
                                patchedValue = { ...toBePatched };
                            }
                            (patchedValue as Record<string, unknown>)[k] = newValue;
                        }
                    } else if (
                        (oldValue === null || typeof oldValue !== "object")
                    ) {
                        if (patchedValue === toBePatched) {
                            patchedValue = { ...toBePatched };
                        }
                        (patchedValue as Record<string, unknown>)[k] = v;
                    }
                }
            }
        });
    }
    if (remove) {
        // Apply removals
        Object.entries(remove).forEach(([k, v]) => {
            const idx = Number(k);
            if (RE_NUMBER.test(k) && Array.isArray(toBePatched) && toBePatched.length > idx) {
                const oldValue = (toBePatched as Array<unknown>)[idx];
                if (oldValue !== undefined) {
                    if (v !== null && typeof v === "object" && !Array.isArray(v)) {
                        const newValue = patchValue(oldValue, undefined, v);
                        if (newValue !== oldValue) {
                            if (patchedValue === toBePatched) {
                                patchedValue = [...toBePatched] as T;
                            }
                            (patchedValue as Array<unknown>)[idx] = newValue;
                        }
                    } else {
                        if (patchedValue === toBePatched) {
                            patchedValue = [...toBePatched] as T;
                        }
                        (patchedValue as Array<unknown>).splice(idx, 1);
                    }
                }
            } else if (toBePatched && typeof toBePatched === "object" && !Array.isArray(toBePatched)) {
                const oldValue = (toBePatched as Record<string, unknown>)[k];
                if (oldValue !== undefined) {
                    if (v !== null && typeof v === "object" && !Array.isArray(v)) {
                        const newValue = patchValue(oldValue, undefined, v);
                        if (newValue !== oldValue) {
                            if (patchedValue === toBePatched) {
                                patchedValue = { ...toBePatched };
                            }
                            (patchedValue as Record<string, unknown>)[k] = newValue;
                        }
                    } else {
                        if (patchedValue === toBePatched) {
                            patchedValue = { ...toBePatched };
                        }
                        delete (patchedValue as Record<string, unknown>)[k];
                    }
                }
            }
        });
    }
    return patchedValue;
};
