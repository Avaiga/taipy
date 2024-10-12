import React from "react";
import Alert from "@mui/material/Alert";
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface NotificationProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message?: string;
    defaultMessage?: string;
    variant?: "filled" | "outlined" ; 
}

const Notification = (props: NotificationProps) => {
    const severity = props.severity || "error";
    const message = useDynamicProperty(props.message, props.defaultMessage, "");
    const variant = props.variant || "filled"; 

    return (
        <Alert severity={severity} variant={variant} id={props.id} className={props.className}>
            {message}
        </Alert>
    );
};

export default Notification;
