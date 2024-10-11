import React from "react";
import Alert from "@mui/material/Alert";
import { TaipyBaseProps } from "./utils";
import { useDynamicProperty } from "../../utils/hooks";

interface NotificationProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message?: string;
    defaultMessage?: string;
}

const Notification = (props: NotificationProps) => {
    const severity = props.severity || "error";
    const message = useDynamicProperty(props.message, props.defaultMessage, "");

    return (
        <Alert severity={severity} id={props.id} className={props.className}>
            {message}
        </Alert>
    );
};

export default Notification;
