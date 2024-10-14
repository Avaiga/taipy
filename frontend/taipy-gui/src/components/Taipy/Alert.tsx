import React from "react";
import Alert from "@mui/material/Alert";
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface NotificationProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message?: string;
    defaultMessage?: string;
    variant?: "filled" | "outlined";
    render?: boolean;
}

const Notification = (props: NotificationProps) => {
    const render = useDynamicProperty(props.render, true, true);
    const severity = useDynamicProperty(props.severity, "error", "error");
    const variant = useDynamicProperty(props.variant, "filled", "filled");
    const message = useDynamicProperty(props.message, props.defaultMessage, "");

    if (!render) return null; // Don't render if the render prop is false

    return (
        <Alert severity={severity} variant={variant} id={props.id} className={props.className}>
            {message}
        </Alert>
    );
};

export default Notification;
