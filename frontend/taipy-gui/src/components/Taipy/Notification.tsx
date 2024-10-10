import React from "react";
import Alert from "@mui/material/Alert";  
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface NotificationProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message: string | (() => string);  // Dynamic string handling
    variant?: "filled" | "outlined" | "standard";
    defaultMessage?: string;
}

const Notification = (props: NotificationProps) => {
    const { severity = "info", variant = "filled" } = props;

    // Use useDynamicProperty to handle dynamic message and defaultMessage
    let displayMessage = useDynamicProperty(props.message, props.defaultMessage, undefined);

    // Ensure displayMessage is a string
    if (typeof displayMessage === "function") {
        displayMessage = displayMessage();
    }

    return (
        <Alert severity={severity} variant={variant} id={props.id} className={props.className}>
            {displayMessage}
        </Alert>
    );
};

export default Notification;
