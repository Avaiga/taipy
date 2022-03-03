import React, { useMemo } from "react";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";

import { TaipyFieldProps } from "./utils";
import { formatWSValue } from "../../utils";
import { useDynamicProperty, useFormatConfig } from "../../utils/hooks";

const Field = (props: TaipyFieldProps) => {
    const { className, id, dataType, format, defaultValue } = props;
    const formatConfig = useFormatConfig();

    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);

    const value = useMemo(() => {
        return formatWSValue(
            props.value !== undefined ? props.value : defaultValue || "",
            dataType,
            format,
            formatConfig
        );
    }, [defaultValue, props.value, dataType, format, formatConfig]);

    return (
        <Tooltip title={hover || ""}>
            <Typography className={className} id={id} component="span">
                {value}
            </Typography>
        </Tooltip>
    );
};

export default Field;
