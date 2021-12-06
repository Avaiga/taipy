import React, { useCallback, useContext, useEffect, useMemo } from "react";
import Snackbar from "@mui/material/Snackbar";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import MuiAlert, { AlertColor } from "@mui/material/Alert";

import { AlertMessage, createAlertAction } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

interface AlertProps {
    alert?: AlertMessage;
}

const Alert = (props: AlertProps) => {
    const { alert } = props;
    const { dispatch } = useContext(TaipyContext);

    const resetAlert = useCallback(() => dispatch(createAlertAction()), [dispatch]);

    const alertAction = useMemo(
        () => (
            <IconButton size="small" aria-label="close" color="inherit" onClick={resetAlert}>
                <CloseIcon fontSize="small" />
            </IconButton>
        ),
        [resetAlert]
    );

    const faviconUrl = useMemo(() => {
        const nodeList = document.getElementsByTagName("link");
        for (let i = 0; i < nodeList.length; i++) {
            if ((nodeList[i].getAttribute("rel") == "icon") || (nodeList[i].getAttribute("rel") == "shortcut icon")) {
                return nodeList[i].getAttribute("href") || "/favicon.png";
            }
        }
        return "/favicon.png";
    
    }, []);

    useEffect(() => {
        alert && new Notification(document.title || "Taipy", {body: alert.message, icon: faviconUrl})
    }, [alert, faviconUrl]);

    useEffect(() => {
        window.Notification && Notification.requestPermission();
    }, []);

    if (alert) {
        return (
            <Snackbar open={true} autoHideDuration={5000} onClose={resetAlert} action={alertAction}>
                <MuiAlert
                    onClose={resetAlert}
                    severity={alert.atype as AlertColor}
                    sx={{ width: "100%" }}
                    variant="filled"
                    elevation={6}
                >
                    {alert.message}
                </MuiAlert>
            </Snackbar>
        );
    }
    return null;
};

export default Alert;