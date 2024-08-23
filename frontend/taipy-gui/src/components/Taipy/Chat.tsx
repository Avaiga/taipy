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
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import Popper from "@mui/material/Popper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Send from "@mui/icons-material/Send";
import ArrowDownward from "@mui/icons-material/ArrowDownward";
import ArrowUpward from "@mui/icons-material/ArrowUpward";

// import InfiniteLoader from "react-window-infinite-loader";

import { createRequestInfiniteTableUpdateAction, createSendActionNameAction } from "../../context/taipyReducers";
import { TaipyActiveProps, disableColor, getSuffixedClassNames } from "./utils";
import { useClassNames, useDispatch, useDynamicProperty, useElementVisible, useModule } from "../../utils/hooks";
import { LoVElt, useLovListMemo } from "./lovUtils";
import { IconAvatar, avatarSx } from "../../utils/icon";
import { emptyArray, getInitials } from "../../utils";
import { RowType, TableValueType } from "./tableUtils";
import { Stack } from "@mui/material";

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
const avatarColSx = { width: 1.5 * avatarWidth, minWidth: 1.5 * avatarWidth };
const senderMsgSx = {
    width: "fit-content",
    maxWidth: "80%",
    color: (theme: Theme) => theme.palette.text.disabled,
} as SxProps<Theme>;
const gridSx = { pb: "1em", mt: "unset", flex: 1, overflow: "auto" };
const loadMoreSx = { width: "fit-content", marginLeft: "auto", marginRight: "auto" };
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
    color: (theme: Theme) => theme.palette.text.disabled,
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
const noAnchorSx = { overflowAnchor: "none", "& *": { overflowAnchor: "none" } } as SxProps<Theme>;
const anchorSx = { overflowAnchor: "auto", height: "1px", width: "100%" } as SxProps<Theme>;

interface key2Rows {
    key: string;
}

interface ChatRowProps {
    senderId: string;
    message: string;
    name: string;
    className?: string;
    getAvatar: (id: string, sender: boolean) => ReactNode;
    index: number;
}

const ChatRow = (props: ChatRowProps) => {
    const { senderId, message, name, className, getAvatar, index } = props;
    const sender = senderId == name;
    const avatar = getAvatar(name, sender);
    return (
        <Grid
            item
            container
            className={getSuffixedClassNames(className, sender ? "-sent" : "-received")}
            xs={12}
            sx={noAnchorSx}
            justifyContent={sender ? "flex-end" : undefined}
        >
            <Grid item sx={sender ? senderMsgSx : undefined}>
                {avatar ? (
                    <Stack>
                        <Stack direction="row" gap={1}>
                            <Box sx={avatarColSx}></Box>
                            <Box sx={nameSx}>{name}</Box>
                        </Stack>
                        <Stack direction="row" gap={1}>
                            <Box sx={avatarColSx}>{avatar}</Box>
                            <Paper sx={sender ? senderPaperSx : otherPaperSx} data-idx={index}>
                                {message}
                            </Paper>
                        </Stack>
                    </Stack>
                ) : (
                    <Paper sx={sender ? senderPaperSx : otherPaperSx} data-idx={index}>
                        {message}
                    </Paper>
                )}
            </Grid>
        </Grid>
    );
};

const getChatKey = (start: number, page: number) => `Chat-${start}-${start + page}`;

const Chat = (props: ChatProps) => {
    const { id, updateVarName, senderId = "taipy", onAction, withInput = true, defaultKey = "", pageSize = 50 } = props;
    const dispatch = useDispatch();
    const module = useModule();

    const [rows, setRows] = useState<RowType[]>([]);
    const page = useRef<key2Rows>({ key: defaultKey });
    const [columns, setColumns] = useState<Array<string>>([]);
    const scrollDivRef = useRef<HTMLDivElement>(null);
    const anchorDivRef = useRef<HTMLElement>(null);
    const isAnchorDivVisible = useElementVisible(anchorDivRef);
    const [showMessage, setShowMessage] = useState(false);
    const [anchorPopup, setAnchorPopup] = useState<HTMLDivElement | null>(null);

    const className = useClassNames(props.libClassName, props.dynamicClassName, props.className);
    const active = useDynamicProperty(props.active, props.defaultActive, true);
    const hover = useDynamicProperty(props.hoverText, props.defaultHoverText, undefined);
    const users = useLovListMemo(props.users, props.defaultUsers || "");

    const boxSx = useMemo(
        () =>
            props.height
                ? ({
                      ...defaultBoxSx,
                      maxHeight: "" + Number(props.height) == "" + props.height ? props.height + "px" : props.height,
                      display: "flex",
                      flexDirection: "column",
                  } as SxProps<Theme>)
                : defaultBoxSx,
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
        (id: string, sender: boolean) =>
            avatars[id] ||
            (sender ? null : (
                <Tooltip title={id}>
                    <Avatar sx={chatAvatarSx}>{getInitials(id)}</Avatar>
                </Tooltip>
            )),
        [avatars]
    );

    const loadMoreItems = useCallback(
        (startIndex: number) => {
            const key = getChatKey(startIndex, pageSize);
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
                    undefined,
                    true // reverse
                )
            );
        },
        [pageSize, updateVarName, id, dispatch, module]
    );

    const showBottom = useCallback(() => {
        anchorDivRef.current?.scrollIntoView();
        setShowMessage(false);
    }, []);

    const refresh = typeof props.messages === "number";

    useEffect(() => {
        if (!refresh && props.messages && page.current.key && props.messages[page.current.key] !== undefined) {
            const newValue = props.messages[page.current.key];
            if (newValue.rowcount == 0) {
                setRows(emptyArray);
            } else {
                const nr = newValue.data as RowType[];
                if (Array.isArray(nr) && nr.length > newValue.start && nr[newValue.start]) {
                    setRows((old) => {
                        old.length && nr.length > old.length && setShowMessage(true);
                        if (nr.length < old.length) {
                            return nr.concat(old.slice(nr.length));
                        }
                        if (old.length > newValue.start) {
                            return old.slice(0, newValue.start).concat(nr.slice(newValue.start));
                        }
                        return nr;
                    });
                    const cols = Object.keys(nr[newValue.start]);
                    setColumns(cols.length > 2 ? cols : cols.length == 2 ? [...cols, ""] : ["", ...cols, "", ""]);
                }
            }
            page.current.key = getChatKey(0, pageSize);
        }
    }, [refresh, pageSize, props.messages]);

    useEffect(() => {
        if (showMessage && !isAnchorDivVisible) {
            setAnchorPopup(scrollDivRef.current);
            setTimeout(() => setShowMessage(false), 5000);
        } else if (!showMessage) {
            setAnchorPopup(null);
        }
    }, [showMessage, isAnchorDivVisible]);

    useEffect(() => {
        if (refresh) {
            setTimeout(() => loadMoreItems(0), 1); // So that the state can be changed
        }
    }, [refresh, loadMoreItems]);

    useEffect(() => {
        loadMoreItems(0);
    }, [loadMoreItems]);

    const loadOlder = useCallback(
        (evt: MouseEvent<HTMLElement>) => {
            const { start } = evt.currentTarget.dataset;
            if (start) {
                loadMoreItems(parseInt(start));
            }
        },
        [loadMoreItems]
    );

    return (
        <Tooltip title={hover || ""}>
            <Paper className={className} sx={boxSx} id={id}>
                <Grid container rowSpacing={2} sx={gridSx} ref={scrollDivRef}>
                    {rows.length && !rows[0] ? (
                        <Grid item className={getSuffixedClassNames(className, "-load")} xs={12} sx={noAnchorSx}>
                            <Box sx={loadMoreSx}>
                                <Button
                                    endIcon={<ArrowUpward />}
                                    onClick={loadOlder}
                                    data-start={rows.length - rows.findIndex((row) => !!row)}
                                >
                                    Load More
                                </Button>
                            </Box>
                        </Grid>
                    ) : null}
                    {rows.map((row, idx) =>
                        row ? (
                            <ChatRow
                                key={columns[0] ? `${row[columns[0]]}` : `id${idx}`}
                                senderId={senderId}
                                message={`${row[columns[1]]}`}
                                name={columns[2] ? `${row[columns[2]]}` : "Unknown"}
                                className={className}
                                getAvatar={getAvatar}
                                index={idx}
                            />
                        ) : null
                    )}
                    <Box sx={anchorSx} ref={anchorDivRef} />
                </Grid>
                <Popper id={id} open={Boolean(anchorPopup)} anchorEl={anchorPopup} placement="right">
                    <Chip
                        label="A new message is available"
                        variant="outlined"
                        onClick={showBottom}
                        icon={<ArrowDownward />}
                    />
                </Popper>
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
