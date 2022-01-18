import { MouseEvent } from "react";

export interface TaipyBaseProps {
    id?: string;
    tp_varname?: string;
    className?: string;
    propagate?: boolean;
    tp_updatevars?: string;
    defaultActive?: boolean;
    active?: boolean;
}

export interface TaipyMultiSelectProps {
    selected?: number[];
}

export interface TaipyFieldProps extends TaipyBaseProps {
    dataType?: string;
    value: string | number;
    defaultValue?: string;
    format?: string;
}

export interface TaipyInputProps extends TaipyBaseProps {
    type: string;
    value: string;
    defaultValue?: string;
}

export interface TaipyImage {
    path: string;
    text: string;
}

export const getArrayValue = <T,>(arr: T[], idx: number, defVal?: T): T | undefined =>
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
