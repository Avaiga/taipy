import { formatWSValue } from "../../utils/index";

export const setValueForVarName = (varName: string | string[], props: Record<string, any>, setVal: (a: any) => void, dataType?: string) => {
    if (varName) {
        if (!Array.isArray(varName)) {
            varName = [varName];
        }
        const value = varName.map((n, idx) => idx === 0 ? "tp_" + n.replaceAll(".", "__") : n).reduce((obj: any, n: string) => obj && obj[n], props);
        if (typeof value !== "undefined") {
            setVal(dataType ? formatWSValue(value, dataType): value);
            return true;
        }
    }
    return false;
};

export interface TaipyBaseProps {
    id: string;
    value: string;
    tp_varname: string;
    className?: string;
}

export interface TaipyFieldProps extends TaipyBaseProps {
    dataType: string;
}

export interface TaipyInputProps extends TaipyBaseProps {
    type: string;
    actionName: string;
}
