/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { SnackbarKey, useSnackbar, VariantType } from "notistack";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

import { AlertMessage, createDeleteAlertAction } from "../../context/taipyReducers";
import { useDispatch } from "../../utils/hooks";

interface AlertProps {
    alerts: AlertMessage[];
}

const Alert = ({ alerts }: AlertProps) => {
    const alert = alerts.length ? alerts[0] : undefined;
    const lastKey = useRef<SnackbarKey>("");
    const { enqueueSnackbar, closeSnackbar } = useSnackbar();
    const dispatch = useDispatch();

    const resetAlert = useCallback(
        (key: SnackbarKey) => () => {
            closeSnackbar(key);
        },
        [closeSnackbar]
    );

    const notifAction = useCallback(
        (key: SnackbarKey) => (
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
            if (alert.atype === "") {
                if (lastKey.current) {
                    closeSnackbar(lastKey.current);
                    lastKey.current = "";
                }
            } else {
                lastKey.current = enqueueSnackbar(alert.message, {
                    variant: alert.atype as VariantType,
                    action: notifAction,
                    autoHideDuration: alert.duration,
                });
                alert.system && new Notification(document.title || "Taipy", { body: alert.message, icon: faviconUrl });
            }
            dispatch(createDeleteAlertAction());
        }
    }, [alert, enqueueSnackbar, closeSnackbar, notifAction, faviconUrl, dispatch]);

    useEffect(() => {
        alert?.system && window.Notification && Notification.requestPermission();
    }, [alert?.system]);

    return null;
};

export default Alert;
