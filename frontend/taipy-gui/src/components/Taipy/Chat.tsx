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

import React, { useMemo, useCallback, KeyboardEvent, MouseEvent } from "react";
import { SxProps, Theme, darken, lighten } from "@mui/material/styles";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Send from "@mui/icons-material/Send";

import { createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyActiveProps, disableColor, getSuffixedClassNames } from "./utils";
import {
    useClassNames,
    useDispatch,
    useDispatchRequestUpdateOnFirstRender,
    useDynamicProperty,
    useModule,
} from "../../utils/hooks";
import { LoVElt, useLovListMemo } from "./lovUtils";
import { IconAvatar, avatarSx } from "../../utils/icon";
import { getInitials } from "../../utils";

export type Message = [string, string, string];

interface ChatProps extends TaipyActiveProps {
    messages?: Message[];
    withInput?: boolean;
    users?: LoVElt[];
    defaultUsers?: string;
    onAction?: string;
    senderId?: string;
    height?: string;
}

const ENTER_KEY = "Enter";
const NoMessages: Message[] = [];

const indicWidth = 0.7;
const avatarWidth = 24;
const chatAvatarSx = { ...avatarSx, width: avatarWidth, height: avatarWidth };
const avatarColSx = { width: 1.5 * avatarWidth };
const senderMsgSx = { width: "fit-content", maxWidth: "80%", marginLeft: "auto" };
const gridSx = { pb: "1em" };
const inputSx = { maxWidth: "unset" };
const nameSx = { fontSize: "0.6em", fontWeight: "bolder" };
const senderPaperSx = {
    pr: `${indicWidth}em`,
    pl: `${indicWidth}em`,
    mr: `${indicWidth}em`,
    position: "relative",
    "&:before": {
        content: "''",
        position: "absolute",
        width: "0",
        height: "0",
        borderTopWidth: `${indicWidth}em`,
        borderTopStyle: "solid",
        borderTopColor: (theme: Theme) => theme.palette.background.paper,
        borderLeft: `${indicWidth}em solid transparent`,
        borderRight: `${indicWidth}em solid transparent`,
        top: "0",
        right: `-${indicWidth}em`,
    },
} as SxProps<Theme>;
const otherPaperSx = {
    position: "relative",
    pl: `${indicWidth}em`,
    pr: `${indicWidth}em`,
    "&:before": {
        content: "''",
        position: "absolute",
        width: "0",
        height: "0",
        borderTopWidth: `${indicWidth}em`,
        borderTopStyle: "solid",
        borderTopColor: (theme: Theme) => theme.palette.background.paper,
        borderLeft: `${indicWidth}em solid transparent`,
        borderRight: `${indicWidth}em solid transparent`,
        top: "0",
        left: `-${indicWidth}em`,
    },
} as SxProps<Theme>;
const defaultBoxSx = {
    pl: `${indicWidth}em`,
    pr: `${indicWidth}em`,
    backgroundColor: (theme: Theme) =>
        theme.palette.mode == "dark"
            ? lighten(theme.palette.background.paper, 0.05)
            : darken(theme.palette.background.paper, 0.15),
} as SxProps<Theme>;

const Chat = (props: ChatProps) => {
    const { id, updateVarName, senderId = "taipy", onAction, messages = NoMessages, withInput = true } = props;
    const dispatch = useDispatch();
    const module = useModule();

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const users = useLovListMemo(props.users, props.defaultUsers || "");

    useDispatchRequestUpdateOnFirstRender(dispatch, id, module, undefined, updateVarName);

    const boxSx = useMemo(
        () => (props.height ? { ...defaultBoxSx, maxHeight: props.height } : defaultBoxSx),
        [props.height]
    );
    const handleAction = useCallback(
        (evt: KeyboardEvent<HTMLDivElement>) => {
            if (!evt.shiftKey && !evt.ctrlKey && !evt.altKey && ENTER_KEY == evt.key) {
                const elt = evt.currentTarget.querySelector("input");
                if (elt?.value) {
                    dispatch(
                        createSendActionNameAction(id, module, onAction, evt.key, updateVarName, elt?.value, senderId)
                    );
                    elt.value = "";
                }
                evt.preventDefault();
            }
        },
        [updateVarName, onAction, senderId, id, dispatch, module]
    );

    const handleClick = useCallback(
        (evt: MouseEvent<HTMLButtonElement>) => {
            const elt = evt.currentTarget.parentElement?.parentElement?.querySelector("input");
            if (elt?.value) {
                dispatch(
                    createSendActionNameAction(id, module, onAction, "click", updateVarName, elt?.value, senderId)
                );
                elt.value = "";
            }
            evt.preventDefault();
        },
        [updateVarName, onAction, senderId, id, dispatch, module]
    );

    const avatars = useMemo(() => {
        return users.reduce((pv, elt) => {
            if (elt.id) {
                pv[elt.id] =
                    typeof elt.item == "string" ? (
                        <Tooltip title={elt.item}>
                            <Avatar sx={chatAvatarSx}>{getInitials(elt.item)}</Avatar>
                        </Tooltip>
                    ) : (
                        <IconAvatar img={elt.item} sx={chatAvatarSx} />
                    );
            }
            return pv;
        }, {} as Record<string, React.ReactNode>);
    }, [users]);

    const getAvatar = useCallback(
        (id: string) =>
            avatars[id] || (
                <Tooltip title={id}>
                    <Avatar sx={chatAvatarSx}>{getInitials(id)}</Avatar>
                </Tooltip>
            ),
        [avatars]
    );

    return (
        <Tooltip title={hover || ""}>
            <Paper className={className} sx={boxSx} id={id}>
                <Grid container rowSpacing={2} sx={gridSx}>
                    {messages.map((msg) =>
                        senderId == msg[2] ? (
                            <Grid item key={msg[0]} className={getSuffixedClassNames(className, "-sent")} xs={12}>
                                <Box sx={senderMsgSx}>
                                    <Paper sx={senderPaperSx}>{msg[1]}</Paper>
                                </Box>
                            </Grid>
                        ) : (
                            <Grid
                                item
                                container
                                key={msg[0]}
                                className={getSuffixedClassNames(className, "-received")}
                                rowSpacing={0.2}
                                columnSpacing={1}
                            >
                                <Grid item sx={avatarColSx}></Grid>
                                <Grid item sx={nameSx}>
                                    {msg[2]}
                                </Grid>
                                <Box width="100%" />
                                <Grid item sx={avatarColSx}>
                                    {getAvatar(msg[2])}
                                </Grid>
                                <Grid item>
                                    <Paper sx={otherPaperSx}>{msg[1]}</Paper>
                                </Grid>
                            </Grid>
                        )
                    )}
                </Grid>
                {withInput ? (
                    <TextField
                        margin="dense"
                        fullWidth
                        className={getSuffixedClassNames(className, "-input")}
                        label={`message (${senderId})`}
                        disabled={!active}
                        onKeyDown={handleAction}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        aria-label="send message"
                                        onClick={handleClick}
                                        edge="end"
                                        disabled={!active}
                                    >
                                        <Send color={disableColor("primary", !active)} />
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                        sx={inputSx}
                    />
                ) : null}
            </Paper>
        </Tooltip>
    );
};

export default Chat;
