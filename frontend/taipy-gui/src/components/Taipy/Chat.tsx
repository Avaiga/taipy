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

import React, { useMemo, useCallback, KeyboardEvent, MouseEvent, useState, useRef, useEffect, ReactNode } from "react";
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

// import InfiniteLoader from "react-window-infinite-loader";

import { createRequestInfiniteTableUpdateAction, createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyActiveProps, disableColor, getSuffixedClassNames } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useModule } from "../../utils/hooks";
import { LoVElt, useLovListMemo } from "./lovUtils";
import { IconAvatar, avatarSx } from "../../utils/icon";
import { getInitials } from "../../utils";
import { RowType, TableValueType } from "./tableUtils";

interface ChatProps extends TaipyActiveProps {
    messages?: TableValueType;
    withInput?: boolean;
    users?: LoVElt[];
    defaultUsers?: string;
    onAction?: string;
    senderId?: string;
    height?: string;
    defaultKey?: string; // for testing purposes only
    pageSize?: number;
}

const ENTER_KEY = "Enter";

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

interface key2Rows {
    key: string;
}

interface ChatRowProps {
    senderId: string;
    message: string;
    name: string;
    className?: string;
    getAvatar: (id: string) => ReactNode;
}

const ChatRow = ({ senderId, message, name, className, getAvatar }: ChatRowProps) => {
    return senderId == name ? (
        <Grid item className={getSuffixedClassNames(className, "-sent")} xs={12}>
            <Box sx={senderMsgSx}>
                <Paper sx={senderPaperSx}>{message}</Paper>
            </Box>
        </Grid>
    ) : (
        <Grid
            item
            container
            className={getSuffixedClassNames(className, "-received")}
            rowSpacing={0.2}
            columnSpacing={1}
        >
            <Grid item sx={avatarColSx}></Grid>
            <Grid item sx={nameSx}>
                {name}
            </Grid>
            <Box width="100%" />
            <Grid item sx={avatarColSx}>
                {getAvatar(name)}
            </Grid>
            <Grid item>
                <Paper sx={otherPaperSx}>{message}</Paper>
            </Grid>
        </Grid>
    );
};

const Chat = (props: ChatProps) => {
    const { id, updateVarName, senderId = "taipy", onAction, withInput = true, defaultKey = "", pageSize = 50 } = props;
    const dispatch = useDispatch();
    const module = useModule();

    const [rows, setRows] = useState<RowType[]>([]);
    const page = useRef<key2Rows>({ key: defaultKey });
    const [rowCount, setRowCount] = useState(1000); // need something > 0 to bootstrap the infinite loader
    // const [visibleStartIndex, setVisibleStartIndex] = useState(0);
    // const infiniteLoaderRef = useRef<InfiniteLoader>(null);
    const [columns, setColumns] = useState<Array<string>>([]);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const users = useLovListMemo(props.users, props.defaultUsers || "");

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

    const loadMoreItems = useCallback(
        (startIndex: number) => {
            const key = `Chat-${startIndex}-${startIndex + pageSize}`;
            page.current = {
                key: key,
            };
            dispatch(
                createRequestInfiniteTableUpdateAction(
                    updateVarName,
                    id,
                    module,
                    [],
                    key,
                    startIndex,
                    startIndex + pageSize,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    true // reverse
                )
            );
        },
        [pageSize, updateVarName, id, dispatch, module]
    );

    const refresh = typeof props.messages === "number";

    useEffect(() => {
        if (!refresh && props.messages && page.current.key && props.messages[page.current.key] !== undefined) {
            const newValue = props.messages[page.current.key];
            setRowCount(newValue.rowcount);
            const nr = newValue.data as RowType[];
            if (Array.isArray(nr) && nr.length > newValue.start) {
                setRows(nr);
                const cols = Object.keys(nr[0]);
                setColumns(cols.length > 2 ? cols : cols.length == 2 ? [...cols, ""] : ["", ...cols, "", ""]);
            }
        }
    }, [refresh, props.messages]);

    useEffect(() => {
        if (refresh) {
            setRows([]);
            setTimeout(() => loadMoreItems(0), 1); // So that the state can be changed
        }
    }, [refresh, loadMoreItems]);

    useEffect(() => {
        loadMoreItems(0);
    }, [loadMoreItems]);

    return (
        <Tooltip title={hover || "" || `rowCount: ${rowCount}`}>
            <Paper className={className} sx={boxSx} id={id}>
                <Grid container rowSpacing={2} sx={gridSx}>
                    {rows.map((row, idx) => (
                        <ChatRow
                            key={columns[0] ? `${row[columns[0]]}` : `id${idx}`}
                            senderId={senderId}
                            message={`${row[columns[1]]}`}
                            name={columns[2] ? `${row[columns[2]]}` : "A"}
                            className={className}
                            getAvatar={getAvatar}
                        />
                    ))}
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
