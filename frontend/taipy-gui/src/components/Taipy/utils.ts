/*
 * Copyright 2023 Avaiga Private Limited
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

import { MouseEvent } from "react";

export interface TaipyActiveProps extends TaipyDynamicProps, TaipyHoverProps {
    defaultActive?: boolean;
    active?: boolean;
}

export interface TaipyHoverProps {
    hoverText?: string;
    defaultHoverText?: string;
}

interface TaipyDynamicProps extends TaipyBaseProps {
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

export interface TaipyMultiSelectProps {
    selected?: number[];
}

export interface TaipyChangeProps {
    onChange?: string;
}

export interface TaipyInputProps extends TaipyActiveProps, TaipyChangeProps, TaipyLabelProps {
    type: string;
    value: string;
    defaultValue?: string;
    changeDelay?: number;
    onAction?: string;
    actionKeys?: string;
    multiline?: boolean;
    linesShown?: number;
}

export interface TaipyLabelProps {
    label?: string;
}

export const getArrayValue = <T>(arr: T[], idx: number, defVal?: T): T | undefined => {
    const val = Array.isArray(arr) && idx < arr.length ? arr[idx] : undefined;
    return val ?? defVal;
};

/**
 * Extracts the backend name of a property.
 *
 * @param updateVars - The value held by the property *updateVars*.
 * @param name - The name of a bound property.
 * @returns The backend-generated variable name.
 */
export const getUpdateVar = (updateVars: string, name: string) => {
    const sel = updateVars && updateVars.split(";").find((uv) => uv && uv.startsWith(name + "="));
    if (sel) {
        return sel.substring(name.length + 1);
    }
    return sel;
};

export const getUpdateVars = (updateVars?: string) =>
    updateVars
        ? updateVars
              .split(";")
              .filter((uv) => uv && uv.indexOf("=") > -1)
              .map((uv) => uv.split("=")[1].trim())
        : [];

export const doNotPropagateEvent = (event: MouseEvent) => event.stopPropagation();

export const noDisplayStyle = { display: "none" };

const RE_ONLY_NUMBERS = /^\d+(\.\d*)?$/;
export const getCssSize = (val: string | number) => {
    if (typeof val === "number") {
        return "" + val + "px";
    } else {
        val = val.trim();
        if (RE_ONLY_NUMBERS.test(val)) {
            return val + "px";
        }
    }
    return val;
};

export const getSuffixedClassNames = (names: string | undefined, suffix: string) =>
    (names || "")
        .split(/\s+/)
        .map((n) => n + suffix)
        .join(" ");
