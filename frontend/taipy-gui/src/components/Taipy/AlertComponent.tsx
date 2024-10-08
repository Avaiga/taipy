import React, { useCallback, useMemo } from "react";
import Alert from "@mui/material/Alert";
import { TaipyBaseProps } from "./utils";
import { useClassNames } from "../../utils/hooks";

interface AlertComponentProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message: string;
    variant?: "filled" | "outlined" | "standard";
}

const AlertComponent = (props: AlertComponentProps) => {
   
    const { severity = "info", message, variant = "filled" } = props;

    // Handle className using a custom hook, if applicable
    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);

    // Memoize the severity and message rendering to optimize performance
    const renderAlert = useCallback(() => {
        return (
            <Alert severity={severity} variant={variant} id={props.id} className={className}>
                {message}
            </Alert>
        );
    }, [severity, message, variant, className, props.id]);

    // Use useMemo to potentially optimize complex rendering, though here it's simple
    return useMemo(() => renderAlert(), [renderAlert]);
};

export default AlertComponent;
