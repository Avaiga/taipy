import React, { useState, useEffect } from "react";
import Typography from "@mui/material/Typography";

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
        <Typography className={className} id={id} component="span">
            {value}
        </Typography>
    );
};

export default Field;
