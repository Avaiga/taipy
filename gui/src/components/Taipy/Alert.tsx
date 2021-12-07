import React, { useCallback, useContext, useEffect, useMemo } from "react";
import { useSnackbar, VariantType } from "notistack";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

import { AlertMessage, createAlertAction } from "../../context/taipyReducers";
import { TaipyContext } from "../../context/taipyContext";

interface AlertProps {
    alert?: AlertMessage;
}

const Alert = (props: AlertProps) => {
    const { alert } = props;
    const { dispatch } = useContext(TaipyContext);
    const { enqueueSnackbar, closeSnackbar } = useSnackbar();

    const resetAlert = useCallback(
        (key: string) => () => {
            closeSnackbar(key);
            dispatch(createAlertAction());
        },
        [dispatch, closeSnackbar]
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
                autoHideDuration: 3000,
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
