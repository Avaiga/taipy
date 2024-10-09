import React from "react";
import Alert from "@mui/material/Alert";  
import { TaipyBaseProps } from "./utils";

interface AlertComponentProps extends TaipyBaseProps {
    severity?: "error" | "warning" | "info" | "success";
    message: string | (() => string);  // Dynamic string handling
    variant?: "filled" | "outlined" | "standard";
}

const AlertComponent = (props: AlertComponentProps) => {  
    const { severity = "info", message, variant = "filled" } = props;

    // Handle dynamic string by checking if `message` is a function and calling it
    const displayMessage = typeof message === "function" ? message() : message;

    return (
        <Alert severity={severity} variant={variant} id={props.id} className={props.className}>
            {displayMessage}
        </Alert>
    );
};

export default AlertComponent;
