export interface TaipyBaseProps {
    id: string;
    defaultValue: string;
    tp_varname: string;
    className?: string;
    value: unknown;
    propagate: boolean;
    tp_updatevars: string;
    active: boolean;
}

export interface TaipyMultiSelect {
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

export const getUpdateVar = (updateVars: string, name: string) => {
    const sel = updateVars && updateVars.split(";").find((uv) => uv && uv.startsWith(name + "="));
    if (sel) {
        return sel.substring(name.length + 1);
    }
    return sel;
};

export const getUpdateVars = (updateVars: string) =>
    updateVars
        ? updateVars
              .split(";")
              .filter((uv) => uv && uv.indexOf("=") > -1)
              .map((uv) => uv.split("=")[1].trim())
        : [];
