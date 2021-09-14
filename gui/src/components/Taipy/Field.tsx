import React, { useState, useEffect } from "react";

import { setValueForVarName, TaipyFieldProps } from "./utils";
import { formatWSValue } from "../../utils";

const Field = (props: TaipyFieldProps) => {
    const { className, id, tp_varname, dataType } = props;
    const [value, setValue] = useState(() => formatWSValue(props.value, dataType));

    useEffect(() => {
        setValueForVarName(tp_varname, props, setValue, dataType);
    }, [tp_varname, props, dataType]);

    return (
        <span className={className} id={id}>
            {value}
        </span>
    );
};

export default Field;
