export interface TaipyBaseProps {
    id: string;
    defaultValue: string;
    tp_varname: string;
    className?: string;
    value: unknown;
    propagate: boolean;
    tp_updatevars: string;
}

export interface TaipyFieldProps extends TaipyBaseProps {
    dataType: string;
    value: string;
    format: string;
}

export interface TaipyInputProps extends TaipyBaseProps {
    type: string;
    actionName: string;
    value: string;
}

export interface TaipyImage {
    path: string;
    text: string;
}
