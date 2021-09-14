import { formatWSValue } from "../../utils/index";

export const setValueForVarName = (varName: string, props: Record<string, any>, setVal: (a: any) => void, dataType?: string) => {
    if (varName) {
        const fullKey = "tp_" + varName.replaceAll(".", "__");
        if (typeof props[fullKey] !== "undefined") {
            setVal(dataType ? formatWSValue(props[fullKey], dataType): props[fullKey]);
        }
    }
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
