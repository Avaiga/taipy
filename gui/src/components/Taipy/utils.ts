export interface TaipyBaseProps {
    id: string;
    defaultValue: string;
    tp_varname: string;
    className?: string;
    value: unknown;
    propagate: boolean;
    tp_updatevars: string;
}

export interface TaipyMultiSelect {
    defaultSelected: string;
    selected: number[];
}

export interface TaipyFieldProps extends TaipyBaseProps {
    dataType: string;
    value: string;
    format: string;
}

export interface TaipyInputProps extends TaipyBaseProps {
    type: string;
    tp_onAction: string;
    value: string;
}

export interface TaipyImage {
    path: string;
    text: string;
}

export const getArrayValue = <T extends unknown>(arr: T[], idx: number, defVal?: T): T | undefined =>
    (arr && idx < arr.length && arr[idx]) || defVal;
