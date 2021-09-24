import React, { useState, useEffect } from "react";
import Typography from "@mui/material/Typography";

import { TaipyFieldProps } from "./utils";
import { formatWSValue } from "../../utils";

const Field = (props: TaipyFieldProps) => {
    const { className, id, dataType, format } = props;
    const [value, setValue] = useState(() => formatWSValue(props.defaultvalue, dataType, format));

    useEffect(() => {
        if (props.value !== undefined) {
            setValue(formatWSValue(props.value, dataType, format))
        }
    }, [props.value, dataType, format]);

    return (
        <Typography className={className} id={id} component="span">
            {value}
        </Typography>
    );
};

export default Field;
