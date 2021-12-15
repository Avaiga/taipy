import React, { useCallback, useEffect, useMemo } from "react";
import { useSnackbar, VariantType } from "notistack";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

import { AlertMessage } from "../../context/taipyReducers";

interface AlertProps {
    alert?: AlertMessage;
}

const Alert = (props: AlertProps) => {
    const { alert } = props;
    const { enqueueSnackbar, closeSnackbar } = useSnackbar();

    const resetAlert = useCallback(
        (key: string) => () => {
            closeSnackbar(key);
        },
        [closeSnackbar]
    );

    const notifAction = useCallback(
        (key: string) => (
            <IconButton size="small" aria-label="close" color="inherit" onClick={resetAlert(key)}>
                <CloseIcon fontSize="small" />
            </IconButton>
        ),
        [resetAlert]
    );

    const faviconUrl = useMemo(() => {
        const nodeList = document.getElementsByTagName("link");
        for (let i = 0; i < nodeList.length; i++) {
            if (nodeList[i].getAttribute("rel") == "icon" || nodeList[i].getAttribute("rel") == "shortcut icon") {
                return nodeList[i].getAttribute("href") || "/favicon.png";
            }
        }
        return "/favicon.png";
    }, []);

    useEffect(() => {
        if (alert) {
            enqueueSnackbar(alert.message, {
                variant: alert.atype as VariantType,
                action: notifAction,
                autoHideDuration: alert.duration,
            });
            alert.browser && new Notification(document.title || "Taipy", { body: alert.message, icon: faviconUrl });
        }
    }, [alert, enqueueSnackbar, notifAction, faviconUrl]);

    useEffect(() => {
        alert?.browser && window.Notification && Notification.requestPermission();
    }, [alert?.browser]);

    return null;
};

export default Alert;
