import React, { useMemo } from "react";
import Typography from "@mui/material/Typography";

import { TaipyFieldProps } from "./utils";
import { formatWSValue } from "../../utils";
import { useFormatConfig } from "../../utils/hooks";

const Field = (props: TaipyFieldProps) => {
    const { className, id, dataType, format, defaultValue } = props;
    const formatConfig = useFormatConfig();

    const value = useMemo(() => {
        return formatWSValue(
            props.value !== undefined ? props.value : defaultValue || "",
            dataType,
            format,
            formatConfig
        );
    }, [defaultValue, props.value, dataType, format, formatConfig]);

    return (
        <Typography className={className} id={id} component="span">
            {value}
        </Typography>
    );
};

export default Field;
