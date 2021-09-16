import React, { useState, useEffect } from "react";

import { TaipyFieldProps } from "./utils";
import { formatWSValue } from "../../utils";

const Field = (props: TaipyFieldProps) => {
    const { className, id, dataType } = props;
    const [value, setValue] = useState(() => formatWSValue(props.defaultvalue, dataType));

    useEffect(() => {
        if (typeof props.value !== 'undefined') {
            setValue(dataType ? formatWSValue(props.value, dataType) : props.value)
        }
    }, [props.value, dataType]);

    return (
        <span className={className} id={id}>
            {value}
        </span>
    );
};

export default Field;
