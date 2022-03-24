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
    className?: string;
}

export interface TaipyMultiSelectProps {
    selected?: number[];
}

export interface TaipyChangeProps {
    tp_onChange?: string;
}

export interface TaipyFieldProps extends TaipyBaseProps, TaipyHoverProps {
    dataType?: string;
    value: string | number;
    defaultValue?: string;
    format?: string;
}

export interface TaipyInputProps extends TaipyActiveProps, TaipyChangeProps {
    type: string;
    value: string;
    defaultValue?: string;
}

export const getArrayValue = <T>(arr: T[], idx: number, defVal?: T): T | undefined =>
    (arr && idx < arr.length && arr[idx]) || defVal;

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

export const getSuffixedClassNames = (names: string | undefined, suffix: string) => (names || "").split(/\s+/).map(n => n+suffix).join(" ")
