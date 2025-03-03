/*
 * Copyright 2021-2025 Avaiga Private Limited
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

import React, { useCallback, useEffect, useMemo, useRef, SyntheticEvent } from "react";
import { SnackbarKey, useSnackbar, VariantType, CloseReason } from "notistack";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

import { NotificationMessage, createDeleteNotificationAction } from "../../context/taipyReducers";
import { useDispatch } from "../../utils/hooks";

interface NotificationProps {
    notifications: NotificationMessage[];
}

const TaipyNotification = ({ notifications: notificationProps }: NotificationProps) => {
    const notification = notificationProps.length ? notificationProps[0] : undefined;
    const { enqueueSnackbar, closeSnackbar } = useSnackbar();
    const snackbarIds = useRef<Record<string, string>>({});
    const dispatch = useDispatch();

    const closeNotifications = useCallback(
        (ids: string[]) => {
            ids.forEach((id) => closeSnackbar(id));
        },
        [closeSnackbar]
    );

    const notificationAction = useCallback(
        (key: SnackbarKey) => (
            <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={() => closeNotifications([key as string])}
            >
                <CloseIcon fontSize="small" />
            </IconButton>
        ),
        [closeNotifications]
    );

    const notificationClosed = (event: SyntheticEvent | null, reason: CloseReason, key?: SnackbarKey) => {
        snackbarIds.current = Object.fromEntries(Object.entries(snackbarIds.current).filter(([id]) => id !== key));
    };

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
        if (notification) {
            const notificationId = notification.notificationId;
            if (notification.nType === "") {
                if (notificationId) {
                    closeNotifications(
                        Object.entries(snackbarIds.current)
                            .filter(([, id]) => notificationId === id)
                            .map(([snackbarId]) => snackbarId)
                    );
                }
            } else {
                if (notificationId) {
                    snackbarIds.current = {
                        ...snackbarIds.current,
                        [notification.snackbarId]: notificationId,
                    };
                }
                enqueueSnackbar(notification.message, {
                    variant: notification.nType as VariantType,
                    action: notificationAction,
                    onClose: notificationClosed,
                    key: notification.snackbarId,
                    autoHideDuration: notification.duration || null,
                });
                notification.system &&
                    new Notification(document.title || "Taipy", { body: notification.message, icon: faviconUrl });
            }
            dispatch(createDeleteNotificationAction(notification.snackbarId));
        }
    }, [notification, enqueueSnackbar, closeNotifications, notificationAction, faviconUrl, dispatch]);

    useEffect(() => {
        notification?.system && window.Notification && Notification.requestPermission();
    }, [notification?.system]);

    return null;
};

export default TaipyNotification;
